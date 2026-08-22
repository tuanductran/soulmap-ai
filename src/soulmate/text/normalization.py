"""Framework-neutral text normalization utilities."""

from __future__ import annotations

import re

RIGHT_SINGLE_QUOTE = "\u2019"


def normalize_text(text: str, *, strip: bool = True) -> str:
    """Normalize smart punctuation and collapse internal whitespace.

    The operation is deterministic and intentionally does not perform locale
    translation, stemming, transliteration, or semantic classification.
    """

    normalized = text.lower().replace(RIGHT_SINGLE_QUOTE, "'").replace("`", "'")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip() if strip else normalized
