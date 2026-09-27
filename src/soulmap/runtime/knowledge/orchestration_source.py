"""Load executable orchestration rules from the orchestration Markdown contract."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_CONTRACT_HEADING = "Runtime execution contract"
_ROW_RE = re.compile(
    r"^\|\s*(?P<name>[^|]+?)\s*\|\s*(?P<value>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class OrchestrationRules:
    """Executable routing values authored in orchestration.md."""

    stage_1_max_user_messages: int
    breakthrough_min_strength: str
    phase_1_safety_before_framework_selection: bool
    template_routing_required: bool


def _contract_body(text: str) -> str:
    match = re.search(rf"^## {re.escape(_CONTRACT_HEADING)}\s*$", text, re.MULTILINE)
    if match is None:
        raise ValueError("Orchestration runtime execution contract is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


@lru_cache(maxsize=1)
def load_orchestration_rules() -> OrchestrationRules:
    """Read and validate executable routing values from shipped Markdown."""
    path = default_skill_path("skills/meta/orchestration.md")
    body = _contract_body(path.read_text(encoding="utf-8"))
    values: dict[str, str] = {}
    for match in _ROW_RE.finditer(body):
        key = re.sub(r"[^a-z0-9]+", "_", match.group("name").strip().lower()).strip("_")
        if not key or key == "rule":
            continue
        values[key] = match.group("value").strip().lower()
    required = {
        "stage_1_override_maximum_user_messages",
        "breakthrough_override_minimum_insight_strength",
        "phase_1_safety_checks_before_framework_selection",
        "template_routing_required_before_delivery",
    }
    if set(values) != required:
        raise ValueError("Orchestration runtime execution contract is incomplete.")
    try:
        stage_max = int(values["stage_1_override_maximum_user_messages"])
    except ValueError as exc:
        raise ValueError(
            "Stage 1 override maximum user messages must be an integer."
        ) from exc
    strength = values["breakthrough_override_minimum_insight_strength"]
    if strength not in {"emerging", "strong"}:
        raise ValueError("Breakthrough override strength must be emerging or strong.")
    if stage_max < 1:
        raise ValueError("Stage 1 override maximum user messages must be positive.")
    boolean_values: dict[str, bool] = {}
    for key in (
        "phase_1_safety_checks_before_framework_selection",
        "template_routing_required_before_delivery",
    ):
        value = values[key]
        if value not in {"true", "false"}:
            raise ValueError(key + " must be true or false.")
        boolean_values[key] = value == "true"
    return OrchestrationRules(
        stage_max,
        strength,
        boolean_values["phase_1_safety_checks_before_framework_selection"],
        boolean_values["template_routing_required_before_delivery"],
    )
