"""Canonical shipped-member contract shared by all artifact tooling."""

from __future__ import annotations

import fnmatch
from pathlib import Path

CORE_FILES = ("LICENSE", "SOULMAP.md", "SKILL.md")
PLUGIN_PREFIX = ".claude-plugin/"

# Agent/developer entrypoints belong to the working repository, never to the
# portable knowledge package. Match case-insensitively wherever they appear.
EXCLUDED_ENTRYPOINT_NAMES = frozenset(
    {
        "agents.md",
        "claude.md",
        "gemini.md",
        "codex.md",
        "copilot.md",
        "copilot-instructions.md",
        "copilot_instructions.md",
        "cursor.md",
        ".cursorrules",
        "cursorrules",
        "aider.md",
        "qwen.md",
        "warp.md",
        "cody.md",
        "opencode.md",
    }
)
EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".claude",
        ".cursor",
        ".github",
        ".vscode",
        ".idea",
        ".venv",
        "__pycache__",
    }
)
EXCLUDED_ENTRYPOINT_PREFIXES = frozenset(
    {
        "agents",
        "claude",
        "gemini",
        "codex",
        "copilot",
        "cursor",
        "aider",
        "qwen",
        "warp",
        "cody",
        "opencode",
    }
)


def is_excluded_entrypoint_name(name: str) -> bool:
    """Return whether a filename is reserved for repository agent instructions."""
    normalized = name.casefold()
    return normalized in EXCLUDED_ENTRYPOINT_NAMES or (
        normalized.endswith(".md")
        and normalized.split(".", maxsplit=1)[0] in EXCLUDED_ENTRYPOINT_PREFIXES
    )


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


def is_excluded_source(path: Path, repo_root: Path) -> bool:
    """Return whether a source file is an agent entrypoint or local config."""
    relative = path.relative_to(repo_root)
    if is_excluded_entrypoint_name(relative.name):
        return True
    return any(
        part.casefold() in EXCLUDED_DIRECTORY_NAMES for part in relative.parts[:-1]
    )


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
            if path.is_file() and not is_excluded_source(path, repo_root)
        )

    if include_plugin:
        plugin_root = repo_root / ".claude-plugin"
        if plugin_root.is_dir():
            paths.extend(
                path
                for path in plugin_root.rglob("*")
                if path.is_file() and not is_excluded_source(path, repo_root)
            )

    return sorted(set(paths))


def source_members(repo_root: Path, *, include_plugin: bool) -> set[str]:
    """Return the canonical set of members allowed in a shipped artifact."""
    patterns = load_distignore(repo_root)
    return {
        path.relative_to(repo_root).as_posix()
        for path in source_paths(repo_root, include_plugin=include_plugin)
        if not is_ignored(path.relative_to(repo_root).as_posix(), patterns)
    }
