"""Load integration-celebration runtime detection knowledge from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from soulmap.runtime.knowledge.keyword_lists import (
    load_key_value_table,
    load_labeled_groups,
)
from soulmap.runtime.knowledge.labels import CELEBRATION_GUIDANCE_NAMES, map_label
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_CONTRACT_HEADING = "Detection policy"
_SCORE_WEIGHTS = {
    "win or completion": 3,
    "relief after difficulty": 3,
    "gratitude": 2,
    "recognized progress": 2,
}
_DETECTION_THRESHOLD = 2
_NEGATIVE_OVERRIDE_PENALTY = 2
_STRENGTH_THRESHOLD = 4
_CONFIRMATION_SCORE = 2


@dataclass(frozen=True, slots=True)
class CelebrationRules:
    """Runtime scoring rules plus semantic signal lists from Markdown."""

    score_weights: dict[str, int]
    threshold: int
    negative_override_penalty: int
    strength_threshold: int
    confirmation_score: int
    negative_overrides: tuple[str, ...]
    confirmation_signals: tuple[str, ...]
    confirmation_assistant_anchors: tuple[str, ...]
    signal_groups: dict[str, tuple[str, ...]]
    guidance: dict[str, str]


def _contract_body(text: str) -> str:
    match = re.search(
        rf"^## {re.escape(_CONTRACT_HEADING)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("Celebration detection policy is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _section_body(body: str, heading: str) -> str:
    match = re.search(rf"^### {re.escape(heading)}\s*$", body, re.MULTILINE)
    if match is None:
        raise ValueError(f"Celebration section {heading!r} is missing.")
    remainder = body[match.end() :]
    next_heading = re.search(r"^###\s+", remainder, re.MULTILINE)
    return remainder[: next_heading.start()] if next_heading else remainder


def _quoted_bullets(body: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(re.findall(r'^- "([^"]+)"\s*$', body, re.MULTILINE)))


def _knowledge_lists(body: str) -> dict[str, tuple[str, ...]]:
    """Load semantic signal lists authored for AI-facing guidance."""
    return {
        "NEGATIVE_OVERRIDES": _quoted_bullets(
            _section_body(body, "Negative overrides")
        ),
        "CONFIRMATION_SIGNALS": _quoted_bullets(
            _section_body(body, "Confirmation signals")
        ),
        "CONFIRMATION_ASSISTANT_ANCHORS": _quoted_bullets(
            _section_body(body, "Confirmation assistant anchors")
        ),
    }


@lru_cache(maxsize=1)
def load_celebration_rules() -> CelebrationRules:
    """Load semantic signal lists and combine them with Python-owned scoring rules."""
    path = runtime_skill_path("integration-celebration")
    body = _contract_body(path.read_text(encoding="utf-8"))
    values = _knowledge_lists(body)
    groups = load_labeled_groups(path, "Detection signals")
    guidance_labels = load_key_value_table(path, "Guidance")
    guidance = {
        map_label(label, CELEBRATION_GUIDANCE_NAMES, "Celebration guidance"): value
        for label, value in guidance_labels.items()
    }
    required_guidance = {"not_detected", "detected", "closing"}
    if not required_guidance <= guidance.keys():
        raise ValueError("Celebration guidance configuration is incomplete.")
    return CelebrationRules(
        score_weights=_SCORE_WEIGHTS,
        threshold=_DETECTION_THRESHOLD,
        negative_override_penalty=_NEGATIVE_OVERRIDE_PENALTY,
        strength_threshold=_STRENGTH_THRESHOLD,
        confirmation_score=_CONFIRMATION_SCORE,
        negative_overrides=cast(tuple[str, ...], values["NEGATIVE_OVERRIDES"]),
        confirmation_signals=cast(tuple[str, ...], values["CONFIRMATION_SIGNALS"]),
        confirmation_assistant_anchors=cast(
            tuple[str, ...], values["CONFIRMATION_ASSISTANT_ANCHORS"]
        ),
        signal_groups=groups,
        guidance=guidance,
    )
