"""Shared static detector configuration blocks."""

from __future__ import annotations

from .safety import (
    DECISION_SEEKING,
    DEPENDENCY_KEYWORDS,
    HIGH_DEPENDENCY_THRESHOLD,
    ISOLATION_SIGNALS,
    MODERATE_DEPENDENCY_THRESHOLD,
)

__all__ = [
    "DECISION_SEEKING",
    "DEPENDENCY_KEYWORDS",
    "HIGH_DEPENDENCY_THRESHOLD",
    "ISOLATION_SIGNALS",
    "MODERATE_DEPENDENCY_THRESHOLD",
]
