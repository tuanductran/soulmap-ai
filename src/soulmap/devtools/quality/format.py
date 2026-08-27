from __future__ import annotations

import argparse
import subprocess

from soulmap.devtools.support.markdown import iter_markdown_files
from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.devtools.support.run import (
    python_executable,
    python_module,
    repo_tooling_lock,
    run,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Format Python and Markdown files across the repo."
    )
    parser.parse_args(argv)
    repo_root = REPO_ROOT
    python = python_executable(repo_root)
    python_paths = [
        str(path)
        for path in (
            repo_root / "src",
            repo_root / "tests",
            repo_root / "scripts",
        )
        if path.exists()
    ]

    with repo_tooling_lock(repo_root):
        python_module("ruff", "check", "--fix", *python_paths, cwd=repo_root)
        python_module("ruff", "format", *python_paths, cwd=repo_root)

        md_files = iter_markdown_files(repo_root)
        if md_files:
            rel_md_files = [
                str(p.resolve().relative_to(repo_root.resolve())) for p in md_files
            ]
            result = run(
                [
                    python,
                    "-m",
                    "pymarkdown",
                    "--config",
                    ".pymarkdown.json",
                    "fix",
                    *rel_md_files,
                ],
                cwd=repo_root,
                check=False,
            )
            if result.returncode not in (0, 3):
                raise subprocess.CalledProcessError(
                    result.returncode,
                    result.args,
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
