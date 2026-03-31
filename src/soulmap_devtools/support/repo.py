from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _looks_like_repo_root(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "pyproject.toml").exists()
        and (path / "src").exists()
        and (path / "AGENTS.md").exists()
    )


def resolve_repo_root() -> Path:
    env_candidates = [
        os.environ.get("SOULMAP_REPO_ROOT"),
        os.environ.get("GITHUB_WORKSPACE"),
        os.environ.get("CODEX_PROJECT_DIR"),
        os.environ.get("CLAUDE_PROJECT_DIR"),
    ]
    for candidate in env_candidates:
        if not candidate:
            continue
        path = Path(candidate).resolve()
        if _looks_like_repo_root(path):
            return path

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if _looks_like_repo_root(candidate):
            return candidate

    for candidate in Path(__file__).resolve().parents:
        if _looks_like_repo_root(candidate):
            return candidate

    return Path(__file__).resolve().parents[3]


REPO_ROOT = resolve_repo_root()
PYTHON_SOURCE_DIR_NAMES = ("src", "tests", "scripts")


def python_source_paths(repo_root: Path) -> list[Path]:
    return [
        repo_root / name
        for name in PYTHON_SOURCE_DIR_NAMES
        if (repo_root / name).exists()
    ]


def tracked_hygiene_violations(repo_root: Path) -> list[str]:
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        return []

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )
    violations: list[str] = []
    for rel_path in result.stdout.splitlines():
        path = Path(rel_path)
        parts = path.parts
        if any(part == "__pycache__" for part in parts):
            violations.append(rel_path)
            continue
        if path.name.endswith((".pyc", ".pyo")):
            violations.append(rel_path)
            continue
        if any(part.endswith((".egg-info", ".dist-info")) for part in parts):
            violations.append(rel_path)
            continue
        if any(part in {".pytest_cache", ".ruff_cache"} for part in parts):
            violations.append(rel_path)
    return violations
