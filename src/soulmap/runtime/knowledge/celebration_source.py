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
    """Load and validate semantic signal lists authored for AI-facing guidance."""
    values = {
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
    for key, items in values.items():
        if not items or not all(isinstance(item, str) and item for item in items):
            raise ValueError(f"Celebration setting {key} is invalid.")
    return values


@lru_cache(maxsize=1)
def load_celebration_rules() -> CelebrationRules:
    """Load semantic signal lists and combine them with Python-owned scoring rules."""
    path = runtime_skill_path("integration-celebration")
    body = _contract_body(path.read_text(encoding="utf-8"))
    values = _knowledge_lists(body)
    scoring = load_key_value_table(path, "Scoring approach")

    def scoring_value(label: str) -> int:
        try:
            value = int(scoring[label])
        except (KeyError, ValueError) as exc:
            raise ValueError(f"Celebration scoring setting {label!r} is invalid.") from exc
        if value < 0:
            raise ValueError(f"Celebration scoring setting {label!r} cannot be negative.")
        return value

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
        score_weights={
            "win or completion": scoring_value("Win or completion weight"),
            "relief after difficulty": scoring_value("Relief after difficulty weight"),
            "gratitude": scoring_value("Gratitude weight"),
            "recognized progress": scoring_value("Recognized progress weight"),
        },
        threshold=scoring_value("Detection threshold"),
        negative_override_penalty=scoring_value("Negative override penalty"),
        strength_threshold=scoring_value("Strength threshold"),
        confirmation_score=scoring_value("Confirmation score"),
        negative_overrides=cast(tuple[str, ...], values["NEGATIVE_OVERRIDES"]),
        confirmation_signals=cast(tuple[str, ...], values["CONFIRMATION_SIGNALS"]),
        confirmation_assistant_anchors=cast(
            tuple[str, ...], values["CONFIRMATION_ASSISTANT_ANCHORS"]
        ),
        signal_groups=groups,
        guidance=guidance,
    )
