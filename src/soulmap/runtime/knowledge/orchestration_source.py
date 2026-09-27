"""Load the executable orchestration contract from the orchestration skill."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_CONTRACT_RE = re.compile(
    r"^## Runtime execution contract\s*(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_BLOCK_RE = re.compile(
    r"\x60\x60\x60python\s*(?P<body>.*?)\x60\x60\x60",
    re.MULTILINE | re.DOTALL,
)
_EXPECTED_PRIORITY = (
    "CRISIS",
    "DEPENDENCY",
    "DE_ESCALATION_HIGH",
    "GRIEF",
    "DE_ESCALATION_MODERATE",
    "EXISTENTIAL",
    "INNER_PARTS",
    "DIRECTION",
    "CREATIVE_DROUGHT",
    "PERFECTIONISM_PARALYSIS",
    "SHADOW",
    "ANCESTRAL_PATTERNS",
    "FEAR_OF_VISIBILITY",
    "EMPATH_BOUNDARY",
    "DARK_NIGHT_OF_SOUL",
    "SOUL_NOURISHMENT",
    "DIVINE_GUIDANCE",
    "SACRED_POLARITY",
    "SPIRITUAL_PURPOSE",
    "SOULMATE_LONGING",
    "PARTNERSHIP_PATTERNS",
    "MEANING_INTEGRATION",
    "INTEGRATION_CELEBRATION",
    "SYNTHESIS",
    "PATTERN",
    "MIRROR",
)


@dataclass(frozen=True, slots=True)
class OrchestrationRules:
    """Validated executable settings from the orchestration knowledge."""

    primary_priority: tuple[str, ...]
    stage_1_override_max_user_messages: int
    stage_1_override_framework: str
    breakthrough_framework: str
    secondary_layers: tuple[str, ...]
    mode_rules: dict[str, str]


def parse_orchestration(text: str) -> OrchestrationRules:
    """Parse and validate the runtime execution contract."""
    match = _CONTRACT_RE.search(text)
    if match is None:
        raise ValueError("Orchestration runtime execution contract is missing.")
    block = _BLOCK_RE.search(match.group("body"))
    if block is None:
        raise ValueError("Orchestration runtime execution configuration is missing.")
    values: dict[str, object] = {}
    tree = ast.parse(block.group("body"), mode="exec")
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                values[target.id] = ast.literal_eval(node.value)
    required = {
        "PRIMARY_PRIORITY",
        "STAGE_1_OVERRIDE_MAX_USER_MESSAGES",
        "STAGE_1_OVERRIDE_FRAMEWORK",
        "BREAKTHROUGH_FRAMEWORK",
        "SECONDARY_LAYERS",
        "MODE_RULES",
    }
    if set(values) != required:
        raise ValueError("Orchestration runtime configuration is incomplete.")
    priority = values["PRIMARY_PRIORITY"]
    if not isinstance(priority, tuple) or priority != _EXPECTED_PRIORITY:
        raise ValueError("Orchestration primary priority is incomplete or invalid.")
    max_messages = values["STAGE_1_OVERRIDE_MAX_USER_MESSAGES"]
    if not isinstance(max_messages, int) or max_messages < 1:
        raise ValueError("Stage 1 override message count is invalid.")
    stage_framework = values["STAGE_1_OVERRIDE_FRAMEWORK"]
    breakthrough = values["BREAKTHROUGH_FRAMEWORK"]
    if not isinstance(stage_framework, str) or not stage_framework:
        raise ValueError("Stage 1 override framework is invalid.")
    if not isinstance(breakthrough, str) or not breakthrough:
        raise ValueError("Breakthrough framework is invalid.")
    secondary = values["SECONDARY_LAYERS"]
    if not isinstance(secondary, tuple) or not secondary:
        raise ValueError("Orchestration secondary layers are invalid.")
    modes = values["MODE_RULES"]
    if (
        not isinstance(modes, dict)
        or set(modes) != {"CRISIS", "SANCTUARY", "MIRROR", "PEER"}
        or not all(
            isinstance(key, str) and isinstance(value, str) and value
            for key, value in modes.items()
        )
    ):
        raise ValueError("Orchestration mode rules are invalid.")
    return OrchestrationRules(
        primary_priority=priority,
        stage_1_override_max_user_messages=max_messages,
        stage_1_override_framework=stage_framework,
        breakthrough_framework=breakthrough,
        secondary_layers=secondary,
        mode_rules=modes,
    )


@lru_cache(maxsize=1)
def load_orchestration_rules() -> OrchestrationRules:
    """Load and validate the shipped orchestration contract once per process."""
    path = default_skill_path("skills/meta/orchestration.md")
    return parse_orchestration(path.read_text(encoding="utf-8"))
