from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
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
