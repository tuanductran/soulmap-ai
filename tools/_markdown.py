from __future__ import annotations

from pathlib import Path

_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "dist",
    "node_modules",
    ".pre-commit-cache",
    ".ruff_cache",
    ".pytest_cache",
    ".cache",
    ".npm",
    ".yarn",
    ".pnpm-store",
}


def iter_markdown_files(repo_root: Path) -> list[Path]:
    md_files: list[Path] = []
    seen_resolved: set[Path] = set()
    for path in repo_root.rglob("*.md"):
        parts = set(path.parts)
        if parts & _EXCLUDED_DIRS:
            continue
        resolved = path.resolve()
        if resolved in seen_resolved:
            continue
        seen_resolved.add(resolved)
        md_files.append(path)
    return sorted(md_files)
