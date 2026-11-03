"""Python-owned executable rules for dependency detection."""

from __future__ import annotations

import re

DEPENDENCY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "only you understand me (really)",
        re.compile(r"\bonly you\s+really\s+understand(?:s)?\s+me\b"),
    ),
    (
        "only you understand me (truly)",
        re.compile(r"\bonly you\s+truly\s+understand(?:s)?\s+me\b"),
    ),
    (
        "you're the only one who understands me (really)",
        re.compile(r"\byou're\s+the\s+only\s+one\s+who\s+really\s+understands\s+me\b"),
    ),
    (
        "you are the only one who understands me (really)",
        re.compile(
            r"\byou\s+are\s+the\s+only\s+one\s+who\s+really\s+understands\s+me\b"
        ),
    ),
    (
        "you're the only one who understands me (truly)",
        re.compile(r"\byou're\s+the\s+only\s+one\s+who\s+truly\s+understands\s+me\b"),
    ),
    (
        "you are the only one who understands me (truly)",
        re.compile(
            r"\byou\s+are\s+the\s+only\s+one\s+who\s+truly\s+understands\s+me\b"
        ),
    ),
)

CONTEXT_EXCLUSION_POLICY = {
    "third-party attribution": False,
    "hypothetical framing": False,
    "negation of an assertion": True,
}
