from __future__ import annotations

import argparse
from pathlib import Path

from soulmap_devtools.support.markdown import iter_markdown_files
from soulmap_devtools.support.repo import (
    REPO_ROOT,
    python_source_paths,
    tracked_hygiene_violations,
)
from soulmap_devtools.support.run import (
    python_executable,
    python_module,
    repo_tooling_lock,
    run,
)


def _pyright_available(repo_root: Path) -> bool:
    python = python_executable(repo_root)
    try:
        run([python, "-m", "pyright", "--version"], cwd=repo_root, check=True)
    except Exception:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m soulmap_devtools.cli.lint")
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
            "soulmap_runtime.guards.markdown_contract",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )
        python_module(
            "soulmap_devtools.cli.check_markdown_links",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )
        python_module(
            "soulmap_devtools.cli.check_markdown_case",
            "--root",
            str(repo_root),
            cwd=repo_root,
        )

        md_files = iter_markdown_files(repo_root)
        if md_files:
            rel_md_files = [
                str(p.resolve().relative_to(repo_root.resolve())) for p in md_files
            ]
            run(
                [
                    python,
                    "-m",
                    "pymarkdown",
                    "--config",
                    ".pymarkdown.json",
                    "scan",
                    *rel_md_files,
                ],
                cwd=repo_root,
            )

        if not args.skip_tests:
            python_module("pytest", "-q", cwd=repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
