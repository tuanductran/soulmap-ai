"""Guardrails against confusable or non-portable punctuation in source files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BANNED_CHARS = {
    "\u2018": "LEFT SINGLE QUOTATION MARK",
    "\u2019": "RIGHT SINGLE QUOTATION MARK",
    "\u201c": "LEFT DOUBLE QUOTATION MARK",
    "\u201d": "RIGHT DOUBLE QUOTATION MARK",
    "\u2013": "EN DASH",
    "\u2014": "EM DASH",
    "\u2026": "HORIZONTAL ELLIPSIS",
    "\u00a0": "NO-BREAK SPACE",
}

TARGET_GLOBS = [
    "CHANGELOG.md",
    "modules/**/*.py",
    "tools/**/*.py",
    "tests/**/*.py",
    "scripts/**/*.py",
    ".claude/**/*.sh",
    ".claude/**/*.json",
    ".claude/**/*.md",
    ".codex/**/*.py",
    ".codex/**/*.json",
    ".codex/**/*.md",
    ".github/workflows/*.yml",
]


def _iter_target_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in TARGET_GLOBS:
        files.update(ROOT.glob(pattern))
    return sorted(path for path in files if path.is_file())


def test_source_and_local_workflow_files_avoid_non_portable_punctuation() -> None:
    violations: list[str] = []

    for path in _iter_target_files():
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for char, label in BANNED_CHARS.items():
                if char in line:
                    violations.append(
                        f"{path.relative_to(ROOT)}:{line_no}: contains {label} ({char.encode('unicode_escape').decode()})"
                    )

    assert not violations, "\n".join(violations)
