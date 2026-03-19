from __future__ import annotations

import argparse
from pathlib import Path

from tools._markdown import iter_markdown_files
from tools._repo import REPO_ROOT
from tools._run import python_executable, python_module, run


def _pyright_available(repo_root: Path) -> bool:
    python = python_executable(repo_root)
    try:
        run([python, "-m", "pyright", "--version"], cwd=repo_root, check=True)
    except Exception:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.lint")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running pytest (useful when tests run in a separate CI step).",
    )
    args = parser.parse_args(argv)

    repo_root = REPO_ROOT
    python = python_executable(repo_root)

    python_module(
        "compileall",
        "-q",
        str(repo_root / "modules"),
        str(repo_root / "tests"),
        str(repo_root / "scripts"),
        str(repo_root / "tools"),
        cwd=repo_root,
    )

    python_module("ruff", "check", str(repo_root), cwd=repo_root)
    python_module("ruff", "format", "--check", str(repo_root), cwd=repo_root)
    python_module(
        "isort",
        "--check-only",
        str(repo_root / "modules"),
        str(repo_root / "tests"),
        str(repo_root / "tools"),
        cwd=repo_root,
    )

    if _pyright_available(repo_root):
        python_module("pyright", cwd=repo_root)

    python_module("modules.markdown_contract", "--root", str(repo_root), cwd=repo_root)

    md_files = iter_markdown_files(repo_root)
    md_files = [
        p
        for p in md_files
        if p.resolve().relative_to(repo_root.resolve()).parts[:1]
        not in {("skills",), ("templates",)}
    ]
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
