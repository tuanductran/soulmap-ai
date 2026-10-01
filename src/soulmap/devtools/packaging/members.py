"""Canonical shipped-member contract shared by all artifact tooling."""

from __future__ import annotations

import fnmatch
from pathlib import Path

CORE_FILES = ("LICENSE", "SOULMAP.md", "SKILL.md")
RUNTIME_PREFIX = "skills/runtime/"
PLUGIN_PREFIX = ".claude-plugin/"


def load_distignore(repo_root: Path) -> list[str]:
    """Load repository packaging exclusion patterns."""
    path = repo_root / ".distignore"
    if not path.is_file():
        return []
    return [
        line
        for raw in path.read_text(encoding="utf-8").splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    ]


def is_ignored(relative: str, patterns: list[str]) -> bool:
    """Return whether a repository-relative path matches an exclusion pattern."""
    return any(fnmatch.fnmatch(relative, pattern) for pattern in patterns)


def source_paths(repo_root: Path, *, include_plugin: bool) -> list[Path]:
    """Return exactly the files the package builder is allowed to ship."""
    paths: list[Path] = []
    for name in CORE_FILES:
        candidate = repo_root / name
        if candidate.is_file():
            paths.append(candidate)

    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        paths.extend(
            path
            for path in skills_root.rglob("*")
            if path.is_file() and not path.relative_to(repo_root).as_posix().startswith(RUNTIME_PREFIX)
        )

    if include_plugin:
        plugin_root = repo_root / ".claude-plugin"
        if plugin_root.is_dir():
            paths.extend(path for path in plugin_root.rglob("*") if path.is_file())

    return sorted(set(paths))


def source_members(repo_root: Path, *, include_plugin: bool) -> set[str]:
    """Return the canonical set of members allowed in a shipped artifact."""
    patterns = load_distignore(repo_root)
    return {
        path.relative_to(repo_root).as_posix()
        for path in source_paths(repo_root, include_plugin=include_plugin)
        if not is_ignored(path.relative_to(repo_root).as_posix(), patterns)
    }
