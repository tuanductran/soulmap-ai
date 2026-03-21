from __future__ import annotations

from tools._markdown import iter_markdown_files
from tools._repo import REPO_ROOT
from tools._run import python_executable, python_module, repo_tooling_lock, run


def main(argv: list[str] | None = None) -> int:
    _ = argv
    repo_root = REPO_ROOT
    python = python_executable(repo_root)

    with repo_tooling_lock(repo_root):
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
            rel_md_files_for_pymarkdown = [
                rel for rel in rel_md_files if not rel.startswith(".claude/rules/")
            ]
            if rel_md_files_for_pymarkdown:
                run(
                    [python, "-m", "pymarkdown", "fix", *rel_md_files_for_pymarkdown],
                    cwd=repo_root,
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
