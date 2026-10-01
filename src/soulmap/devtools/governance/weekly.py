"""Run the deterministic weekly repository governance sequence."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable, Sequence

from soulmap.devtools.support.repo import REPO_ROOT

Command = Sequence[str]
Runner = Callable[..., subprocess.CompletedProcess[str]]

CONTRACT_TESTS = (
    "tests/contract/test_p_level_governance.py",
    "tests/contract/test_dependency_refresh_process_contract.py",
    "tests/contract/test_toolchain_support_contract.py",
)

SAFETY_COMMANDS = (
    ("uv", "run", "soulmap", "markdown-contract", "--root", "."),
    ("uv", "run", "soulmap", "check-links", "--root", "."),
    ("uv", "run", "soulmap", "check-case", "--root", "."),
    ("uv", "run", "soulmap", "lint", "--skip-tests"),
    ("uv", "run", "soulmap", "audit-knowledge"),
    ("uv", "run", "python", "tests/eval_regression/test_safety_evals.py"),
    ("uv", "run", "soulmap", "eval-groups"),
    ("uv", "run", "soulmap", "eval-responses"),
    ("uv", "run", "soulmap", "eval-markdown-contracts"),
)

ARTIFACT_COMMANDS = (
    ("uv", "run", "soulmap", "build"),
    ("uv", "run", "soulmap", "build", "--skill"),
    ("uv", "run", "soulmap", "library-manifest"),
    ("uv", "run", "python", "scripts/verify_artifact_hashes.py"),
    ("uv", "run", "python", "scripts/verify_extracted_artifacts.py"),
)

SUMMARY_LINES = (
    "## Weekly SoulMap governance review",
    "",
    "- P-level governance, dependency-refresh and toolchain contracts passed.",
    "- Locked dependency tree captured in the workflow artifact.",
    "- Safety/knowledge evals, full tests and artifact verification passed.",
    "- This workflow does not update, merge or release dependencies automatically.",
)


def _run(
    command: Command,
    *,
    root: Path,
    runner: Runner = subprocess.run,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run one canonical governance command and stop on failure."""
    return runner(
        list(command),
        cwd=root,
        check=True,
        text=True,
        env=env,
        capture_output=capture_output,
    )


def _write_summary(root: Path) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with Path(summary_path).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(SUMMARY_LINES) + "\n")


def run_weekly_governance(
    root: Path = REPO_ROOT,
    *,
    runner: Runner = subprocess.run,
) -> int:
    """Run the repeatable weekly governance sequence in its canonical order."""
    root = root.resolve()
    evidence = root / "weekly-governance"
    evidence.mkdir(parents=True, exist_ok=True)

    tree = _run(
        ("uv", "tree", "--depth", "1"),
        root=root,
        runner=runner,
        capture_output=True,
    )
    (evidence / "uv-tree.txt").write_text(tree.stdout, encoding="utf-8")
    _run(("uv", "lock", "--check"), root=root, runner=runner)

    _run(
        ("uv", "run", "pytest", "-q", *CONTRACT_TESTS),
        root=root,
        runner=runner,
    )

    for command in SAFETY_COMMANDS:
        _run(command, root=root, runner=runner)

    test_env = os.environ.copy()
    test_env["SOULMAP_PYTEST_SCOPE"] = "full"
    _run(
        ("uv", "run", "python", "scripts/pytest_diagnostics.py"),
        root=root,
        runner=runner,
        env=test_env,
    )
    _run(("uv", "run", "deptry", "."), root=root, runner=runner)

    for command in ARTIFACT_COMMANDS:
        _run(command, root=root, runner=runner)

    _write_summary(root)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run weekly governance from the repository root."""
    if argv:
        raise SystemExit("weekly-governance does not accept arguments")
    try:
        return run_weekly_governance()
    except subprocess.CalledProcessError as exc:
        command = " ".join(exc.cmd)
        print(f"Weekly governance failed: {command} (exit {exc.returncode})")
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
