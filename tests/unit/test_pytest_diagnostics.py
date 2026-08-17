from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "pytest_diagnostics.py"


@pytest.fixture
def diagnostics_module() -> dict[str, object]:
    return runpy.run_path(str(SCRIPT), run_name="pytest_diagnostics_test")


def test_build_test_command_preserves_seed_and_worker_mode(
    diagnostics_module: dict[str, object],
) -> None:
    build_test_command = cast(
        Callable[[int, str], list[str]], diagnostics_module["build_test_command"]
    )
    assert build_test_command(12345, "auto") == [
        "uv",
        "run",
        "soulmap",
        "test",
        "-n",
        "auto",
        "-q",
        "--",
        "--randomly-seed=12345",
    ]
    assert build_test_command(12345, "0")[-3:] == ["-q", "--", "--randomly-seed=12345"]


def test_persist_seed_writes_github_env(
    diagnostics_module: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / "github-env"
    monkeypatch.setenv("GITHUB_ENV", str(env_file))

    persist_seed = cast(Callable[[int], None], diagnostics_module["_persist_seed"])
    persist_seed(9876)

    assert env_file.read_text(encoding="utf-8") == "PYTEST_RANDOMLY_SEED=9876\n"


def test_failure_summary_contains_serial_reproduction(
    diagnostics_module: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    summary_file = tmp_path / "summary"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))

    write_failure_summary = cast(
        Callable[[int, str, int], None], diagnostics_module["_write_failure_summary"]
    )
    write_failure_summary(2468, "auto", 1)

    summary = summary_file.read_text(encoding="utf-8")
    assert "pytest-randomly seed: `2468`" in summary
    assert "pytest-xdist workers: `auto`" in summary
    assert "uv run soulmap test -n 0 -q -- --randomly-seed=2468" in summary


def test_main_returns_test_failure_and_writes_diagnostics(
    diagnostics_module: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / "github-env"
    summary_file = tmp_path / "summary"
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
    monkeypatch.setenv("PYTEST_RANDOMLY_SEED", "1357")
    monkeypatch.setenv("SOULMAP_PYTEST_WORKERS", "auto")
    monkeypatch.setattr(diagnostics_module["platform"], "platform", lambda: "test-os")

    calls: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> SimpleNamespace:
        calls.append(command)
        assert check is False
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr(diagnostics_module["subprocess"], "run", fake_run)

    main = cast(Callable[[], int], diagnostics_module["main"])
    build_test_command = cast(
        Callable[[int, str], list[str]], diagnostics_module["build_test_command"]
    )
    assert main() == 1
    assert calls == [build_test_command(1357, "auto")]
    assert env_file.read_text(encoding="utf-8") == "PYTEST_RANDOMLY_SEED=1357\n"
    assert "seed: `1357`" in summary_file.read_text(encoding="utf-8")
