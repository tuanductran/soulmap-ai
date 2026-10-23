"""Load executable orchestration rules from the orchestration Markdown contract."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_CONTRACT_HEADING = "Routing policy"


@dataclass(frozen=True, slots=True)
class PrimaryPriorityRule:
    """One knowledge-authored primary routing rule."""

    framework: str
    mode: str
    blocked: tuple[str, ...]
    insight_secondary: bool = False
    requires_no_insight: bool = False


@dataclass(frozen=True, slots=True)
class SecondaryPriorityRule:
    """One knowledge-authored secondary-layer rule."""

    name: str


@dataclass(frozen=True, slots=True)
class IntensityFallbackRule:
    """Knowledge-authored fallback for an emotional intensity level."""

    level: str
    framework: str
    mode: str
    allowed_secondary: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OrchestrationRules:
    """Executable routing values authored in orchestration.md."""

    stage_1_max_user_messages: int
    breakthrough_min_strength: str
    phase_1_safety_before_framework_selection: bool
    template_routing_required: bool
    primary_priority: tuple[PrimaryPriorityRule, ...]
    secondary_priority: tuple[SecondaryPriorityRule, ...]
    intensity_fallback: tuple[IntensityFallbackRule, ...]
    peer_min_stage: int
    runtime_instructions: dict[str, str]


def _contract_body(text: str) -> str:
    match = re.search(rf"^## {re.escape(_CONTRACT_HEADING)}\s*$", text, re.MULTILINE)
    if match is None:
        raise ValueError("Orchestration runtime execution contract is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _table_rows(body: str, heading: str) -> list[list[str]]:
    match = re.search(rf"^### {re.escape(heading)}\s*$", body, re.MULTILINE)
    if match is None:
        raise ValueError(f"Orchestration section {heading!r} is missing.")
    section = body[match.end() :]
    next_section = re.search(r"^###\s+", section, re.MULTILINE)
    if next_section:
        section = section[: next_section.start()]
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip().replace("\\|", "|") for cell in stripped[1:-1].split("|")]
        if not cells or all(not cell for cell in cells):
            continue
        if all(set(cell) <= {":", "-", " "} for cell in cells):
            continue
        if cells[0].lower() in {"setting", "priority", "level", "name"}:
            continue
        rows.append(cells)
    return rows


_FRAMEWORK_NAMES = {
    "Grief": "GRIEF",
    "Existential": "EXISTENTIAL",
    "Inner Parts": "INNER_PARTS",
    "Direction": "DIRECTION",
    "De-escalation": "DE_ESCALATION",
    "Creative Drought": "CREATIVE_DROUGHT",
    "Perfectionism Paralysis": "PERFECTIONISM_PARALYSIS",
    "Shadow": "SHADOW",
    "Ancestral Patterns": "ANCESTRAL_PATTERNS",
    "Fear of Visibility": "FEAR_OF_VISIBILITY",
    "Empath Boundary": "EMPATH_BOUNDARY",
    "Dark Night of the Soul": "DARK_NIGHT_OF_SOUL",
    "Soul Nourishment": "SOUL_NOURISHMENT",
    "Divine Guidance": "DIVINE_GUIDANCE",
    "Sacred Polarity": "SACRED_POLARITY",
    "Spiritual Purpose": "SPIRITUAL_PURPOSE",
    "Soulmate Longing": "SOULMATE_LONGING",
    "Partnership Patterns": "PARTNERSHIP_PATTERNS",
    "Integration and Celebration": "INTEGRATION_CELEBRATION",
    "Meaning Integration": "MEANING_INTEGRATION",
    "Synthesis": "SYNTHESIS",
    "Pattern": "PATTERN",
}
_MODE_NAMES = {"Sanctuary": "SANCTUARY", "Mirror": "MIRROR", "Peer": "PEER", "De-escalation": "DE_ESCALATION"}
_SECONDARY_NAMES = {
    "Anger": "anger",
    "Spiritual bypass": "bypass",
    "Somatic": "somatic",
    "Meaning Integration": "meaning_integration",
    "Inner Parts": "inner_parts",
}
_INTENSITY_NAMES = {"High": "HIGH", "Moderate": "MODERATE"}
_INSTRUCTION_NAMES = {
    "Stage 1 override": "Stage 1 override",
    "High emotional intensity": "HIGH intensity",
    "Moderate emotional intensity": "MODERATE intensity",
    "Mirror mode fallback": "MIRROR fallback",
    "Peer mode fallback": "PEER fallback",
}


def _mapped(value: str, mapping: dict[str, str], key: str) -> str:
    try:
        return mapping[value]
    except KeyError as exc:
        raise ValueError(f"{key} contains unknown plain-language value {value!r}.") from exc


def _require_bool(value: str, key: str) -> bool:
    choices = {"true": True, "false": False, "required": True, "not required": False, "allowed": True, "not allowed": False}
    normalized = value.strip().casefold()
    if normalized not in choices:
        raise ValueError(f"{key} must use a recognized plain-language choice.")
    return choices[normalized]


def _require_positive_int(value: str, key: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{key} must be a positive integer.") from exc
    if parsed < 1:
        raise ValueError(f"{key} must be a positive integer.")
    return parsed


def _require_str(value: str, key: str) -> str:
    if not value:
        raise ValueError(f"{key} must be a non-empty string.")
    return value


def _parse_primary_priority(
    rows: list[list[str]],
) -> tuple[PrimaryPriorityRule, ...]:
    if not rows:
        raise ValueError("PRIMARY_PRIORITY must be a non-empty table.")
    rules: list[PrimaryPriorityRule] = []
    for row in rows:
        if len(row) != 6:
            raise ValueError("PRIMARY_PRIORITY rows must contain 6 columns.")
        _, framework, mode, blocked, insight_secondary, no_insight = row
        rules.append(
            PrimaryPriorityRule(
                framework=_mapped(framework, _FRAMEWORK_NAMES, "Primary framework priority"),
                mode=_mapped(mode, _MODE_NAMES, "Primary framework priority"),
                blocked=tuple(
                    _mapped(item.strip(), _FRAMEWORK_NAMES, "Blocked frameworks") for item in blocked.split(",") if item.strip()
                ),
                insight_secondary=_require_bool(
                    insight_secondary, "PRIMARY_PRIORITY.insight_secondary"
                ),
                requires_no_insight=_require_bool(
                    no_insight, "PRIMARY_PRIORITY.requires_no_insight"
                ),
            )
        )
    return tuple(rules)


def _parse_intensity_fallback(
    rows: list[list[str]],
) -> tuple[IntensityFallbackRule, ...]:
    if not rows:
        raise ValueError("INTENSITY_FALLBACK must be a non-empty table.")
    rules: list[IntensityFallbackRule] = []
    for row in rows:
        if len(row) != 4:
            raise ValueError("INTENSITY_FALLBACK rows must contain 4 columns.")
        level, framework, mode, allowed = row
        rules.append(
            IntensityFallbackRule(
                level=_mapped(level, _INTENSITY_NAMES, "Intensity fallback"),
                framework=_mapped(framework, _FRAMEWORK_NAMES, "Intensity fallback"),
                mode=_mapped(mode, _MODE_NAMES, "Intensity fallback"),
                allowed_secondary=tuple(
                    _mapped(item.strip(), _SECONDARY_NAMES, "Allowed secondary layers") for item in allowed.split(",") if item.strip()
                ),
            )
        )
    return tuple(rules)


def _parse_secondary_priority(
    rows: list[list[str]],
) -> tuple[SecondaryPriorityRule, ...]:
    if not rows:
        raise ValueError("SECONDARY_PRIORITY must be a non-empty table.")
    rules: list[SecondaryPriorityRule] = []
    for row in rows:
        if len(row) != 2:
            raise ValueError("SECONDARY_PRIORITY rows must contain 2 columns.")
        _, name = row
        rules.append(
            SecondaryPriorityRule(
                name=_mapped(name, _SECONDARY_NAMES, "Secondary layer priority"),
            )
        )
    return tuple(rules)


@lru_cache(maxsize=1)
def load_orchestration_rules() -> OrchestrationRules:
    """Read and validate executable routing values from shipped Markdown."""
    path = runtime_skill_path("orchestration")
    body = _contract_body(path.read_text(encoding="utf-8"))

    scalar_rows = _table_rows(body, "Operational limits")
    scalars = {row[0]: row[1] for row in scalar_rows if len(row) == 2}
    required_scalars = {
        "Stage 1 override max user messages",
        "Breakthrough minimum insight strength",
        "Phase 1 safety checks before framework selection",
        "Template routing required before delivery",
        "Peer minimum stage",
    }
    if set(scalars) != required_scalars:
        raise ValueError("Orchestration scalar settings are incomplete.")
    strength = _require_str(
        scalars["Breakthrough minimum insight strength"],
        "Breakthrough minimum insight strength",
    )
    if strength not in {"emerging", "strong"}:
        raise ValueError("Breakthrough minimum insight strength is invalid.")

    instruction_rows = _table_rows(body, "Mode guidance")
    if not instruction_rows:
        raise ValueError("Runtime instructions must be a non-empty table.")
    runtime_instructions = {row[0]: row[1] for row in instruction_rows if len(row) == 2}
    required_instruction_labels = set(_INSTRUCTION_NAMES)
    if set(runtime_instructions) != required_instruction_labels or any(
        not value for value in runtime_instructions.values()
    ):
        raise ValueError("Orchestration mode guidance is incomplete.")
    runtime_instructions = {
        _INSTRUCTION_NAMES[label]: value for label, value in runtime_instructions.items()
    }

    primary = _parse_primary_priority(_table_rows(body, "Primary framework priority"))
    secondary = _parse_secondary_priority(_table_rows(body, "Secondary layer priority"))
    intensity_fallback = _parse_intensity_fallback(
        _table_rows(body, "Intensity fallback")
    )
    return OrchestrationRules(
        stage_1_max_user_messages=_require_positive_int(
            scalars["Stage 1 override max user messages"],
            "Stage 1 override max user messages",
        ),
        breakthrough_min_strength=strength,
        phase_1_safety_before_framework_selection=_require_bool(
            scalars["Phase 1 safety checks before framework selection"],
            "Phase 1 safety checks before framework selection",
        ),
        template_routing_required=_require_bool(
            scalars["Template routing required before delivery"],
            "Template routing required before delivery",
        ),
        primary_priority=primary,
        secondary_priority=secondary,
        intensity_fallback=intensity_fallback,
        peer_min_stage=_require_positive_int(
            scalars["Peer minimum stage"],
            "Peer minimum stage",
        ),
        runtime_instructions=runtime_instructions,
    )
