"""Prevent implementation-language leakage from shipped knowledge files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHIPPED_KNOWLEDGE_ROOTS = (ROOT / "skills", ROOT / "templates")

_FORBIDDEN_PATTERNS = (
    re.compile(
        r"\bPython\s+(?:runtime|code|implementation|source|modules?)\b", re.IGNORECASE
    ),
    re.compile(r"\bin\s+Python\b", re.IGNORECASE),
    re.compile(r"\bsrc/soulmap/", re.IGNORECASE),
)


def test_shipped_knowledge_has_no_implementation_language_references() -> None:
    """Knowledge stays implementation-neutral while allowing user-topic terms."""
    violations: list[str] = []

    for root in SHIPPED_KNOWLEDGE_ROOTS:
        for path in root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_PATTERNS:
                if pattern.search(text):
                    violations.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")

    assert not violations, (
        "Shipped knowledge contains implementation-language or repository-path "
        f"references: {violations}"
    )
