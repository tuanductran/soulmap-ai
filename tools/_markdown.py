from __future__ import annotations

from pathlib import Path

_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "dist",
    ".pre-commit-cache",
    ".ruff_cache",
    ".pytest_cache",
}


def iter_markdown_files(repo_root: Path) -> list[Path]:
    md_files: list[Path] = []
    for path in repo_root.rglob("*.md"):
        parts = set(path.parts)
        if parts & _EXCLUDED_DIRS:
            continue
        # Generated bundle.
        if path.name == "AGENTS.md" and path.parent.name == "skills":
            continue
        md_files.append(path)
    return sorted(md_files)
