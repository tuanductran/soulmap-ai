from __future__ import annotations

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from soulmap.devtools.quality import lint as lint_tool
from soulmap.devtools.support import repo as repo_support


@contextmanager
def _noop_lock(_repo_root: Path) -> Iterator[None]:
    yield


def _make_repo_root(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "pyproject.toml").write_text("[project]\nname = 'test'\n", encoding="utf-8")
    (path / "SOULMAP.md").write_text("SoulMap\n", encoding="utf-8")
    (path / "src").mkdir(exist_ok=True)
    return path


def test_repo_root_detection_prefers_valid_environment_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = _make_repo_root(tmp_path / "repo")
    invalid = tmp_path / "invalid"
    invalid.mkdir()
    monkeypatch.setenv("SOULMAP_REPO_ROOT", str(repo_root))
    monkeypatch.setenv("GITHUB_WORKSPACE", str(invalid))

    assert repo_support._looks_like_repo_root(repo_root)
    assert not repo_support._looks_like_repo_root(invalid)
    assert repo_support.resolve_repo_root() == repo_root


def test_tracked_hygiene_returns_empty_without_git_and_flags_all_generated_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert repo_support.tracked_hygiene_violations(tmp_path) == []

    (tmp_path / ".git").mkdir()

    class _Result:
        stdout = "\n".join(
            [
                "src/package/__pycache__/module.pyc",
                "src/package/module.pyo",
                "src/package.egg-info/PKG-INFO",
                "src/package.dist-info/METADATA",
                ".pytest_cache/v/cache/nodeids",
                ".ruff_cache/0.1/cache",
                "src/package/keep.py",
            ]
        )

    monkeypatch.setattr(
        repo_support.subprocess, "run", lambda *_args, **_kwargs: _Result()
    )

    assert repo_support.tracked_hygiene_violations(tmp_path) == [
        "src/package/__pycache__/module.pyc",
        "src/package/module.pyo",
        "src/package.egg-info/PKG-INFO",
        "src/package.dist-info/METADATA",
        ".pytest_cache/v/cache/nodeids",
        ".ruff_cache/0.1/cache",
    ]


def test_pyright_availability_reports_success_and_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(lint_tool, "python_executable", lambda _root: "python")

    def successful_run(args: list[str], **_kwargs: object) -> None:
        calls.append(args)

    monkeypatch.setattr(lint_tool, "run", successful_run)
    assert lint_tool._pyright_available(tmp_path) is True
    assert calls == [["python", "-m", "pyright", "--version"]]

    monkeypatch.setattr(
        lint_tool,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("missing")),
    )
    assert lint_tool._pyright_available(tmp_path) is False


def test_lint_runs_pyright_markdown_and_pytest_when_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in ["src", "tests", "scripts", "docs"]:
        (tmp_path / name).mkdir()
    markdown_file = tmp_path / "docs" / "guide.md"
    markdown_file.write_text("# Guide\n", encoding="utf-8")
    calls: list[tuple[str, tuple[str, ...]]] = []
    run_calls: list[list[str]] = []

    monkeypatch.setattr(lint_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lint_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(lint_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(lint_tool, "_pyright_available", lambda _root: True)
    monkeypatch.setattr(lint_tool, "tracked_hygiene_violations", lambda _root: [])
    monkeypatch.setattr(lint_tool, "iter_markdown_files", lambda _root: [markdown_file])

    def fake_python_module(
        module: str, *extra_args: str, cwd: Path, check: bool = True
    ) -> None:
        _ = cwd, check
        calls.append((module, extra_args))

    monkeypatch.setattr(lint_tool, "python_module", fake_python_module)

    def fake_run(
        args: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        """Record the call and answer like a successful subprocess.

        The Markdown scan reads ``returncode`` to decide whether a chunk
        failed, so the stub has to return a completed process rather than
        None. Returning None here made the scan raise instead of reporting.
        """
        run_calls.append(args)
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(lint_tool, "run", fake_run)

    assert lint_tool.main([]) == 0

    assert ("pyright", ()) in calls
    assert ("pytest", ("-q",)) in calls
    assert run_calls[0][:-1] == [
        "python",
        "-m",
        "pymarkdown",
        "--config",
        ".pymarkdown.json",
        "scan",
    ]
    assert run_calls[0][-1].replace("\\", "/") == "docs/guide.md"
