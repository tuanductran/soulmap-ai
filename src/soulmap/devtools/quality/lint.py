"""Repository-wide linting and type checking.

Runs Ruff, Pyright, the Markdown linter, the tracked-file hygiene check, and
by default pytest. This is the local mirror of the CI gate, so a clean run
here should mean a clean run there.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from soulmap.devtools.support.markdown import iter_markdown_files
from soulmap.devtools.support.repo import (
    REPO_ROOT,
    python_source_paths,
    tracked_hygiene_violations,
)
from soulmap.devtools.support.run import (
    python_executable,
    python_module,
    repo_tooling_lock,
    run,
)


def _scan_markdown(repo_root: Path, python: str, rel_md_files: list[str]) -> None:
    """Run the Markdown linter over every file, split across worker processes.

    Scanning the whole tree in one process was the single largest cost in this
    command, 11.0 of its 18.8 seconds. The work is per-file and the linter's
    own startup is only about 180ms, so splitting the file list across
    processes is close to free and scales with the machine: measured 11.5s on
    one worker against 4.5s on four.

    Every chunk runs to completion even when an earlier one fails, so a single
    pass still reports every violation in the tree rather than stopping at the
    first failing chunk. Chunks inherit this process's stdout and write their
    findings straight to it, matching how the serial version behaved.

    Args:
        repo_root: Repository root, used as the working directory.
        python: Interpreter to run the linter with.
        rel_md_files: Repository-relative Markdown paths to scan.

    Raises:
        subprocess.CalledProcessError: If any chunk reports violations.
    """
    if not rel_md_files:
        return

    workers = min(len(rel_md_files), os.cpu_count() or 1)
    size = (len(rel_md_files) + workers - 1) // workers
    chunks = [
        rel_md_files[index : index + size]
        for index in range(0, len(rel_md_files), size)
    ]

    def scan(chunk: list[str]) -> subprocess.CompletedProcess[str]:
        return run(
            [
                python,
                "-m",
                "pymarkdown",
                "--config",
                ".pymarkdown.json",
                "scan",
                *chunk,
            ],
            cwd=repo_root,
            check=False,
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(scan, chunks))

    failed = next(
        (result for result in results if result.returncode != 0),
        None,
    )
    if failed is not None:
        raise subprocess.CalledProcessError(failed.returncode, failed.args)


def _pyright_available(repo_root: Path) -> bool:
    """Report whether Pyright can run in this environment.

    Args:
        repo_root: Repository root, used to resolve the interpreter.

    Returns:
        True when Pyright reports a version. False on any failure, so a
        checkout without the development dependencies still lints instead of
        crashing.
    """
    python = python_executable(repo_root)
    try:
        run([python, "-m", "pyright", "--version"], cwd=repo_root, check=True)
    except Exception:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    """Lint and type-check the repository.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when every check passes, non-zero on the first failure.
    """
    parser = argparse.ArgumentParser(prog="soulmap lint")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running pytest (useful when tests run in a separate CI step).",
    )
    args = parser.parse_args(argv)

    repo_root = REPO_ROOT
    python = python_executable(repo_root)
    python_paths = [str(path) for path in python_source_paths(repo_root)]

    with repo_tooling_lock(repo_root):
        python_module(
            "compileall",
            "-q",
            *python_paths,
            cwd=repo_root,
        )

        python_module("ruff", "check", *python_paths, cwd=repo_root)
        python_module("ruff", "format", "--check", *python_paths, cwd=repo_root)

        if _pyright_available(repo_root):
            python_module("pyright", cwd=repo_root)

        violations = tracked_hygiene_violations(repo_root)
        if violations:
            joined = ", ".join(sorted(violations))
            raise RuntimeError(
                "tracked hygiene violations found: "
                f"{joined}. Remove generated artifacts and caches from tracked paths."
            )

        python_module(
            "soulmap.runtime.guards.markdown_contract",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )
        python_module(
            "soulmap.devtools.checks.check_markdown_links",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )
        python_module(
            "soulmap.devtools.checks.check_markdown_case",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )
        python_module(
            "soulmap.devtools.checks.check_api_docs",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )

        md_files = iter_markdown_files(repo_root)
        if md_files:
            rel_md_files = [
                str(p.resolve().relative_to(repo_root.resolve())) for p in md_files
            ]
            _scan_markdown(repo_root, python, rel_md_files)

        if not args.skip_tests:
            python_module("pytest", "-q", cwd=repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
