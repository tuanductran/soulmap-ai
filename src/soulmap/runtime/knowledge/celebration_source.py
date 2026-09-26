"""Load integration-celebration runtime detection knowledge from Markdown."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path, load_labeled_groups

_CONTRACT_HEADING = "Runtime detection contract"
_BLOCK_RE = re.compile(
    r"```python\s*(?P<body>.*?)```",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class CelebrationRules:
    """Executable detection configuration authored in integration-celebration.md."""

    score_weights: dict[str, int]
    threshold: int
    negative_override_penalty: int
    strength_threshold: int
    confirmation_score: int
    negative_overrides: tuple[str, ...]
    confirmation_signals: tuple[str, ...]
    confirmation_assistant_anchors: tuple[str, ...]
    signal_groups: dict[str, tuple[str, ...]]


def _contract_body(text: str) -> str:
    match = re.search(
        rf"^## {re.escape(_CONTRACT_HEADING)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("Celebration runtime contract is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _literal_config(body: str) -> dict[str, object]:
    match = _BLOCK_RE.search(body)
    if match is None:
        raise ValueError("Celebration runtime configuration block is missing.")
    tree = ast.parse(match.group("body"), mode="exec")
    values: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        values[target.id] = ast.literal_eval(node.value)
    required = {
        "SCORE_WEIGHTS",
        "THRESHOLD",
        "NEGATIVE_OVERRIDE_PENALTY",
        "STRENGTH_THRESHOLD",
        "CONFIRMATION_SCORE",
        "NEGATIVE_OVERRIDES",
        "CONFIRMATION_SIGNALS",
        "CONFIRMATION_ASSISTANT_ANCHORS",
    }
    if set(values) != required:
        raise ValueError("Celebration runtime configuration is incomplete.")
    weights = values["SCORE_WEIGHTS"]
    if not isinstance(weights, dict) or not all(
        isinstance(key, str) and isinstance(value, int)
        for key, value in weights.items()
    ):
        raise ValueError("Celebration score weights are invalid.")
    for key in (
        "THRESHOLD",
        "NEGATIVE_OVERRIDE_PENALTY",
        "STRENGTH_THRESHOLD",
        "CONFIRMATION_SCORE",
    ):
        if not isinstance(values[key], int):
            raise ValueError(f"Celebration setting {key} is invalid.")
    for key in (
        "NEGATIVE_OVERRIDES",
        "CONFIRMATION_SIGNALS",
        "CONFIRMATION_ASSISTANT_ANCHORS",
    ):
        if not isinstance(values[key], tuple) or not all(
            isinstance(item, str) and item for item in values[key]
        ):
            raise ValueError(f"Celebration setting {key} is invalid.")
    return values


@lru_cache(maxsize=1)
def load_celebration_rules() -> CelebrationRules:
    """Read and validate the runtime contract from shipped Markdown."""
    path = default_skill_path("skills/frameworks/integration-celebration.md")
    body = _contract_body(path.read_text(encoding="utf-8"))
    values = _literal_config(body)
    groups = load_labeled_groups(path, "Detection signals")
    return CelebrationRules(
        score_weights=dict(values["SCORE_WEIGHTS"]),
        threshold=values["THRESHOLD"],
        negative_override_penalty=values["NEGATIVE_OVERRIDE_PENALTY"],
        strength_threshold=values["STRENGTH_THRESHOLD"],
        confirmation_score=values["CONFIRMATION_SCORE"],
        negative_overrides=values["NEGATIVE_OVERRIDES"],
        confirmation_signals=values["CONFIRMATION_SIGNALS"],
        confirmation_assistant_anchors=values["CONFIRMATION_ASSISTANT_ANCHORS"],
        signal_groups=groups,
    )
