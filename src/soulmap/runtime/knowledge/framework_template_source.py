"""Resolve deterministic framework output constraints from Python configuration."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.runtime_config import FRAMEWORK_TEMPLATE_ROWS


@dataclass(frozen=True, slots=True)
class TemplateRule:
    """Output constraints for one framework/mode mapping."""

    framework: str
    mode: str
    word_range: str
    question_rule: str
    source_file: str


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


@lru_cache(maxsize=1)
def load_template_rules() -> tuple[TemplateRule, ...]:
    """Load deterministic output constraints from Python-owned configuration."""
    return tuple(TemplateRule(*row) for row in FRAMEWORK_TEMPLATE_ROWS)


def resolve_template(
    framework: str,
    mode: str,
    context: dict[str, object] | None = None,
) -> dict[str, str]:
    """Resolve the deterministic template contract for a routing selection."""
    context = context or {}
    normalized = _key(framework)
    if normalized == "de_escalation":
        target = (
            "De-escalation (HIGH)"
            if mode == "SANCTUARY"
            else "De-escalation (MODERATE)"
        )
    elif normalized == "grief":
        grief_value = context.get("grief")
        grief_context = grief_value if isinstance(grief_value, dict) else context
        grief_type = str(
            grief_context.get("grief_type", grief_context.get("type", "acute"))
        ).lower()
        target = f"Grief ({grief_type})"
    elif normalized == "mirror":
        target = (
            "Mirror (Stage 1)"
            if context.get("stage_override")
            else "Mirror (emotional)"
        )
    else:
        names = {
            "integration_celebration": "Integration and Celebration",
            "meaning_integration": "Meaning Integration",
            "dark_night_of_soul": "Dark Night of the Soul",
            "fear_of_visibility": "Fear of Visibility",
            "creative_drought": "Creative Drought",
            "empath_boundary": "Empath Boundary",
            "perfectionism_paralysis": "Perfectionism Paralysis",
            "soul_nourishment": "Soul Nourishment",
            "divine_guidance": "Divine Guidance",
            "sacred_polarity": "Sacred Polarity",
            "spiritual_purpose": "Spiritual Purpose",
            "soulmate_longing": "Soulmate Longing",
            "partnership_patterns": "Partnership Patterns",
            "ancestral_patterns": "Ancestral Patterns",
        }
        target = names.get(normalized, framework.replace("_", " ").title())

    for rule in load_template_rules():
        if rule.framework.strip().lower() == target.lower():
            return {
                "name": rule.framework,
                "mode": rule.mode,
                "word_range": rule.word_range,
                "question_rule": rule.question_rule,
                "source_file": rule.source_file,
            }
    raise ValueError(
        f"No framework template mapping exists for {framework!r} in mode {mode!r}."
    )
