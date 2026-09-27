"""Load deterministic framework output constraints from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_ROW_RE = re.compile(
    r"^\|\s*(?P<framework>[^|]+?)\s*\|\s*(?P<mode>[^|]+?)\s*\|\s*"
    r"(?P<word_range>[^|]+?)\s*\|\s*(?P<question_rule>[^|]+?)\s*\|\s*"
    r"(?P<source_file>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)


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
    """Read and validate the core framework/template mapping table."""
    path = default_skill_path("skills/meta/framework-template-map.md")
    text = path.read_text(encoding="utf-8")
    rules = tuple(
        TemplateRule(
            framework=match.group("framework").strip(),
            mode=match.group("mode").strip(),
            word_range=match.group("word_range").strip(),
            question_rule=match.group("question_rule").strip(),
            source_file=match.group("source_file").strip(),
        )
        for match in _ROW_RE.finditer(text)
    )
    if not rules:
        raise ValueError("Framework template mapping table is missing.")
    return rules


def resolve_template(
    framework: str,
    mode: str,
    context: dict[str, object] | None = None,
) -> dict[str, str]:
    """Resolve the deterministic template contract for a routing selection."""
    context = context or {}
    normalized = _key(framework)
    if normalized == "de_escalation":
        target = "De-escalation (HIGH)" if mode == "SANCTUARY" else "De-escalation (MODERATE)"
    elif normalized == "grief":
        grief_context = context.get("grief") if isinstance(context.get("grief"), dict) else context
        grief_type = str(grief_context.get("grief_type", grief_context.get("type", "acute"))).lower()
        target = f"Grief ({grief_type})"
    elif normalized == "mirror":
        target = "Mirror (Stage 1)" if context.get("stage_override") else (
            "Mirror (emotional)" if mode == "MIRROR" else "Mirror (emotional)"
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
