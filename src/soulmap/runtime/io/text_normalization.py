"""SoulMap compatibility boundary for text normalization.

The framework-neutral implementation lives in :mod:`soulmate.text`.
"""

from __future__ import annotations

from soulmate.text import RIGHT_SINGLE_QUOTE, normalize_text

__all__ = ["RIGHT_SINGLE_QUOTE", "normalize_message_text"]


def normalize_message_text(message: str, *, strip: bool = True) -> str:
    """Preserve SoulMap's established message-normalization API."""

    return normalize_text(message, strip=strip)
