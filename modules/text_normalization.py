"""Shared text normalization helpers for detector input handling."""

from __future__ import annotations

import re

RIGHT_SINGLE_QUOTE = "\u2019"


def normalize_message_text(message: str, *, strip: bool = True) -> str:
    """Normalize smart punctuation and collapse internal whitespace."""
    normalized = message.lower().replace(RIGHT_SINGLE_QUOTE, "'").replace("`", "'")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip() if strip else normalized
