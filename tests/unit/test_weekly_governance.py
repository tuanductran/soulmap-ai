"""Tests for the Python-owned weekly governance gate."""

from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

from soulmap.devtools.governance.weekly import (
    ARTIFACT_COMMANDS,
    CONTRACT_TESTS,
    SAFETY_COMMANDS,
    SUMMARY_LINES,
    run_weekly_governance,
)


def test_weekly_governance_preserves_command_order(tmp_path: Path) -> None:
    calls: list[tuple[str, ...]] = []

    def runner(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        calls.append(tuple(command))
        return CompletedProcess(command, 0, stdout="dependency tree\n", stderr="")

    assert run_weekly_governance(tmp_path, runner=runner) == 0

    assert calls == [
        ("uv", "tree", "--depth", "1"),
        ("uv", "lock", "--check"),
        ("uv", "run", "pytest", "-q", *CONTRACT_TESTS),
        *SAFETY_COMMANDS,
        ("uv", "run", "python", "scripts/pytest_diagnostics.py"),
        ("uv", "run", "deptry", "."),
        *ARTIFACT_COMMANDS,
    ]
    assert (tmp_path / "weekly-governance" / "uv-tree.txt").read_text() == (
        "dependency tree\n"
    )


def test_weekly_governance_writes_success_summary(tmp_path: Path, monkeypatch) -> None:
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))

    def runner(command: list[str], **kwargs: object) -> CompletedProcess[str]:
        return CompletedProcess(command, 0, stdout="dependency tree\n", stderr="")

    assert run_weekly_governance(tmp_path, runner=runner) == 0
    assert summary.read_text(encoding="utf-8") == "\n".join(SUMMARY_LINES) + "\n"
