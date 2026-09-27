"""Load executable orchestration rules from the orchestration Markdown contract."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_CONTRACT_HEADING = "Runtime execution contract"
_JSON_RE = re.compile(
    r"^\`\`\`json\s*\n(?P<body>.*?)\n\`\`\`", re.MULTILINE | re.DOTALL
)


@dataclass(frozen=True, slots=True)
class PrimaryPriorityRule:
    """One knowledge-authored primary routing rule."""

    result: str
    detected: str
    framework: str
    mode: str
    blocked: tuple[str, ...]
    insight_secondary: bool = False
    requires_no_insight: bool = False
    requires: str | None = None
    requires_not: str | None = None


@dataclass(frozen=True, slots=True)
class SecondaryPriorityRule:
    """One knowledge-authored secondary-layer rule."""

    name: str
    result: str
    detected: str


@dataclass(frozen=True, slots=True)
class OrchestrationRules:
    """Executable routing values authored in orchestration.md."""

    stage_1_max_user_messages: int
    breakthrough_min_strength: str
    phase_1_safety_before_framework_selection: bool
    template_routing_required: bool
    primary_priority: tuple[PrimaryPriorityRule, ...]
    secondary_priority: tuple[SecondaryPriorityRule, ...]
    peer_min_stage: int


def _contract_body(text: str) -> str:
    match = re.search(rf"^## {re.escape(_CONTRACT_HEADING)}\s*$", text, re.MULTILINE)
    if match is None:
        raise ValueError("Orchestration runtime execution contract is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _load_contract_json(body: str) -> dict[str, object]:
    match = _JSON_RE.search(body)
    if match is None:
        raise ValueError("Orchestration runtime JSON contract is missing.")
    try:
        value = json.loads(match.group("body"))
    except json.JSONDecodeError as exc:
        raise ValueError("Orchestration runtime JSON contract is invalid.") from exc
    if not isinstance(value, dict):
        raise ValueError("Orchestration runtime JSON contract must be an object.")
    return cast(dict[str, object], value)


def _require_str(value: object, key: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string.")
    return value


def _require_bool(value: object, key: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be true or false.")
    return value


def _require_positive_int(value: object, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{key} must be a positive integer.")
    return value


def _parse_primary_priority(value: object) -> tuple[PrimaryPriorityRule, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("PRIMARY_PRIORITY must be a non-empty list.")
    rules: list[PrimaryPriorityRule] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Each PRIMARY_PRIORITY entry must be an object.")
        item = cast(dict[str, object], item)
        result_name = _require_str(item.get("result"), "PRIMARY_PRIORITY.result")
        detected = _require_str(item.get("detected"), "PRIMARY_PRIORITY.detected")
        framework = _require_str(item.get("framework"), "PRIMARY_PRIORITY.framework")
        mode = _require_str(item.get("mode"), "PRIMARY_PRIORITY.mode")
        blocked = item.get("blocked", [])
        if not isinstance(blocked, list) or not all(
            isinstance(v, str) for v in blocked
        ):
            raise ValueError("PRIMARY_PRIORITY blocked values must be strings.")
        for key in ("insight_secondary", "requires_no_insight"):
            if key in item and not isinstance(item[key], bool):
                raise ValueError(f"{key} must be boolean.")
        requires_value = item.get("requires")
        requires_not_value = item.get("requires_not")
        if requires_value is not None and not isinstance(requires_value, str):
            raise ValueError("requires must be a string or null.")
        if requires_not_value is not None and not isinstance(requires_not_value, str):
            raise ValueError("requires_not must be a string or null.")
        rules.append(
            PrimaryPriorityRule(
                result=result_name,
                detected=detected,
                framework=framework,
                mode=mode,
                blocked=tuple(blocked),
                insight_secondary=_require_bool(
                    item.get("insight_secondary", False), "insight_secondary"
                ),
                requires_no_insight=_require_bool(
                    item.get("requires_no_insight", False), "requires_no_insight"
                ),
                requires=requires_value,
                requires_not=requires_not_value,
            )
        )
    return tuple(rules)


def _parse_secondary_priority(value: object) -> tuple[SecondaryPriorityRule, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("SECONDARY_PRIORITY must be a non-empty list.")
    rules: list[SecondaryPriorityRule] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Each SECONDARY_PRIORITY entry must be an object.")
        item = cast(dict[str, object], item)
        name = _require_str(item.get("name"), "SECONDARY_PRIORITY.name")
        result_name = _require_str(item.get("result"), "SECONDARY_PRIORITY.result")
        detected = _require_str(item.get("detected"), "SECONDARY_PRIORITY.detected")
        rules.append(
            SecondaryPriorityRule(name=name, result=result_name, detected=detected)
        )
    return tuple(rules)


@lru_cache(maxsize=1)
def load_orchestration_rules() -> OrchestrationRules:
    """Read and validate executable routing values from shipped Markdown."""
    path = default_skill_path("skills/meta/orchestration.md")
    contract = _load_contract_json(_contract_body(path.read_text(encoding="utf-8")))

    required = {
        "STAGE_1_OVERRIDE_MAX_USER_MESSAGES",
        "BREAKTHROUGH_MIN_INSIGHT_STRENGTH",
        "PHASE_1_SAFETY_CHECKS_BEFORE_FRAMEWORK_SELECTION",
        "TEMPLATE_ROUTING_REQUIRED_BEFORE_DELIVERY",
        "PRIMARY_PRIORITY",
        "SECONDARY_PRIORITY",
        "PEER_MIN_STAGE",
    }
    if set(contract) != required:
        raise ValueError("Orchestration runtime execution contract is incomplete.")

    strength = _require_str(
        contract["BREAKTHROUGH_MIN_INSIGHT_STRENGTH"],
        "BREAKTHROUGH_MIN_INSIGHT_STRENGTH",
    )
    if strength not in {"emerging", "strong"}:
        raise ValueError(
            "BREAKTHROUGH_MIN_INSIGHT_STRENGTH must be emerging or strong."
        )

    return OrchestrationRules(
        stage_1_max_user_messages=_require_positive_int(
            contract["STAGE_1_OVERRIDE_MAX_USER_MESSAGES"],
            "STAGE_1_OVERRIDE_MAX_USER_MESSAGES",
        ),
        breakthrough_min_strength=strength,
        phase_1_safety_before_framework_selection=_require_bool(
            contract["PHASE_1_SAFETY_CHECKS_BEFORE_FRAMEWORK_SELECTION"],
            "PHASE_1_SAFETY_CHECKS_BEFORE_FRAMEWORK_SELECTION",
        ),
        template_routing_required=_require_bool(
            contract["TEMPLATE_ROUTING_REQUIRED_BEFORE_DELIVERY"],
            "TEMPLATE_ROUTING_REQUIRED_BEFORE_DELIVERY",
        ),
        primary_priority=_parse_primary_priority(contract["PRIMARY_PRIORITY"]),
        secondary_priority=_parse_secondary_priority(contract["SECONDARY_PRIORITY"]),
        peer_min_stage=_require_positive_int(
            contract["PEER_MIN_STAGE"], "PEER_MIN_STAGE"
        ),
    )
