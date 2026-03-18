from __future__ import annotations

from tools._markdown import iter_markdown_files
from tools._repo import REPO_ROOT
from tools._run import python_executable, python_module, run


def main(argv: list[str] | None = None) -> int:
    _ = argv
    repo_root = REPO_ROOT
    python = python_executable(repo_root)

    python_module("ruff", "check", "--fix", str(repo_root), cwd=repo_root)
    # Keep isort consistent with `scripts/format.sh` but include `tools/` too.
    python_module(
        "isort",
        str(repo_root / "modules"),
        str(repo_root / "tests"),
        str(repo_root / "tools"),
        cwd=repo_root,
    )
    python_module("ruff", "format", str(repo_root), cwd=repo_root)

    md_files = iter_markdown_files(repo_root)
    if md_files:
        run([python, "-m", "mdformat", *[str(p) for p in md_files]], cwd=repo_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
