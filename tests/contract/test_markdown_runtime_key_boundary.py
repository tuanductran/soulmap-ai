"""Enforce the boundary between skill prose and Python-facing identifiers."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills"
PYTHON_PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
SNAKE_CASE_TOKEN = re.compile(
    r"\b(?:[a-z][a-z0-9]*_[a-z0-9_]+|[A-Z][A-Z0-9]*_[A-Z0-9_]+)\b"
)
MACHINE_KEY_CELL = re.compile(
    r"`?(?:[a-z][a-z0-9]*(?:[_-][a-z0-9]+)+|"
    r"[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)+)`?"
)


def test_skills_do_not_contain_python_format_placeholders() -> None:
    """Dynamic Python formatting belongs outside canonical skill Markdown."""
    violations: list[str] = []
    for path in sorted(SKILLS_ROOT.rglob("*.md")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PYTHON_PLACEHOLDER.search(line):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}"
                )

    assert not violations, "\n".join(violations)


def test_skills_do_not_contain_python_shaped_identifiers() -> None:
    """Key-shaped runtime identifiers must be resolved through config, not Markdown."""
    violations: list[str] = []
    for path in sorted(SKILLS_ROOT.rglob("*.md")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if SNAKE_CASE_TOKEN.search(line):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}"
                )
            if line.lstrip().startswith("|"):
                first_cell = line.strip().strip("|").split("|", 1)[0].strip()
                if MACHINE_KEY_CELL.fullmatch(first_cell):
                    violations.append(
                        f"{path.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}"
                    )

    assert not violations, "\n".join(violations)
