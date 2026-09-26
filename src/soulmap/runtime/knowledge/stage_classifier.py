"""Load the operational stage-classification rules from shipped Markdown.

The stage detector must execute the scoring algorithm authored in
``skills/meta/stage-classifier.md`` rather than carrying a second copy of its
keyword sets, weights, thresholds, or recency multipliers in Python.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_STAGE_RE = re.compile(r"^### Stage (?P<number>[1-6]), (?P<name>.+?)\s*$", re.MULTILINE)
_KEYWORDS_RE = re.compile(
    r"\*\*Keyword signals \(weight: (?P<weight>\d+) each\):\*\*"
    r"(?P<body>.*?)(?=\n\*\*Classification signals:\*\*|\Z)",
    re.DOTALL,
)
_QUOTED_RE = re.compile(r'^- "([^"]+)"\s*$', re.MULTILINE)
_THRESHOLD_RE = re.compile(
    r"^\|\s*(?P<stage>[1-6])\s*\|\s*(?P<threshold>\d+)\s*(?:\([^|]+\))?\s*\|",
    re.MULTILINE,
)
_CONTRACT_HEADING = "Runtime enforcement contract"
_BLOCK_RE = re.compile(
    r"\x60\x60\x60python\s*(?P<body>.*?)\x60\x60\x60", re.MULTILINE | re.DOTALL
)
_MULTIPLIER_RE = re.compile(
    r"^\|\s*Current message\s*\|\s*(?P<current>[0-9.]+)x\s*\|\s*$"
    r"|^\|\s*Previous message\s*\|\s*(?P<previous>[0-9.]+)x\s*\|\s*$"
    r"|^\|\s*2 messages back\s*\|\s*(?P<two_back>[0-9.]+)x\s*\|\s*$"
    r"|^\|\s*3 messages back\s*\|\s*(?P<three_back>[0-9.]+)x\s*\|\s*$"
    r"|^\|\s*4 messages back\s*\|\s*(?P<four_back>[0-9.]+)x\s*\|\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class StageRule:
    """Executable scoring rules for one user-journey stage."""

    number: int
    name: str
    weight: int
    keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StageClassifierRules:
    """Parsed scoring configuration from the stage-classifier skill."""

    stages: tuple[StageRule, ...]
    thresholds: dict[int, int]
    recency_multipliers: tuple[float, ...]
    memory_minimums: dict[str, int]
    close_score_delta: float
    first_session_default_stage: int
    first_session_max_stage: int
    anti_regression_min_lower_stage_messages: int
    stage_roles: dict[int, str]
    stage_recommendations: dict[int, str]


def _display_name(raw_name: str) -> str:
    """Convert the Markdown stage heading into the public display name."""
    return raw_name.replace(" and ", " & ").title()


def _runtime_contract(text: str) -> dict[str, object]:
    match = re.search(
        rf"^## {re.escape(_CONTRACT_HEADING)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("Stage runtime enforcement contract is missing.")
    body = text[match.end() :]
    block = _BLOCK_RE.search(body)
    if block is None:
        raise ValueError("Stage runtime enforcement configuration is missing.")
    tree = ast.parse(block.group("body"), mode="exec")
    values: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                values[target.id] = ast.literal_eval(node.value)
    required = {
        "MEMORY_MINIMUMS",
        "CLOSE_SCORE_DELTA",
        "FIRST_SESSION_DEFAULT_STAGE",
        "FIRST_SESSION_MAX_STAGE",
        "ANTI_REGRESSION_MIN_LOWER_STAGE_MESSAGES",
        "STAGE_ROLES",
        "STAGE_RECOMMENDATIONS",
    }
    if set(values) != required:
        raise ValueError("Stage runtime enforcement configuration is incomplete.")
    if not isinstance(values["MEMORY_MINIMUMS"], dict):
        raise ValueError("Stage memory minimums are invalid.")
    if not all(
        isinstance(key, str) and isinstance(value, int)
        for key, value in values["MEMORY_MINIMUMS"].items()
    ):
        raise ValueError("Stage memory minimums are invalid.")
    for key in (
        "CLOSE_SCORE_DELTA",
        "FIRST_SESSION_DEFAULT_STAGE",
        "FIRST_SESSION_MAX_STAGE",
        "ANTI_REGRESSION_MIN_LOWER_STAGE_MESSAGES",
    ):
        if not isinstance(values[key], (int, float)):
            raise ValueError(f"Stage runtime setting {key} is invalid.")
    for key in ("STAGE_ROLES", "STAGE_RECOMMENDATIONS"):
        value = values[key]
        if not isinstance(value, dict) or set(value) != set(range(1, 7)):
            raise ValueError(f"Stage runtime mapping {key} is incomplete.")
        if not all(isinstance(item, str) and item for item in value.values()):
            raise ValueError(f"Stage runtime mapping {key} is invalid.")
    return values


def parse_stage_classifier(text: str) -> StageClassifierRules:
    """Parse the scoring contract from stage-classifier Markdown.

    Raises:
        ValueError: If a stage, threshold, or recency multiplier is missing.
    """
    matches = list(_STAGE_RE.finditer(text))
    if len(matches) != 6:
        raise ValueError(f"Expected 6 stage definitions, found {len(matches)}.")

    stages: list[StageRule] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end() : end]
        keyword_match = _KEYWORDS_RE.search(section)
        if keyword_match is None:
            raise ValueError(f"Stage {match.group('number')} has no keyword section.")
        keywords = tuple(
            dict.fromkeys(
                value.lower()
                for value in _QUOTED_RE.findall(keyword_match.group("body"))
            )
        )
        if not keywords:
            raise ValueError(f"Stage {match.group('number')} has no keywords.")
        stages.append(
            StageRule(
                number=int(match.group("number")),
                name=_display_name(match.group("name")),
                weight=int(keyword_match.group("weight")),
                keywords=keywords,
            )
        )

    minimums_section_match = re.search(
        r"## Minimum Thresholds(?P<body>.*?)(?=\n## |\Z)", text, re.DOTALL
    )
    if minimums_section_match is None:
        raise ValueError("Stage classifier has no minimum-threshold table.")
    thresholds = {
        int(match.group("stage")): int(match.group("threshold"))
        for match in _THRESHOLD_RE.finditer(minimums_section_match.group("body"))
    }
    if set(thresholds) != set(range(1, 7)):
        raise ValueError("Stage classifier threshold table is incomplete.")

    scoring_section_match = re.search(
        r"## Scoring Algorithm(?P<body>.*?)(?=\n## |\Z)", text, re.DOTALL
    )
    if scoring_section_match is None:
        raise ValueError("Stage classifier has no scoring algorithm section.")
    multipliers: dict[str, float] = {}
    for match in _MULTIPLIER_RE.finditer(scoring_section_match.group("body")):
        for key, value in match.groupdict().items():
            if value is not None:
                multipliers[key] = float(value)
    if set(multipliers) != {
        "current",
        "previous",
        "two_back",
        "three_back",
        "four_back",
    }:
        raise ValueError("Stage classifier recency table is incomplete.")

    contract = _runtime_contract(text)
    return StageClassifierRules(
        stages=tuple(stages),
        thresholds=thresholds,
        recency_multipliers=(
            multipliers["four_back"],
            multipliers["three_back"],
            multipliers["two_back"],
            multipliers["previous"],
            multipliers["current"],
        ),
        memory_minimums=cast(dict[str, int], contract["MEMORY_MINIMUMS"]),
        close_score_delta=float(contract["CLOSE_SCORE_DELTA"]),
        first_session_default_stage=int(contract["FIRST_SESSION_DEFAULT_STAGE"]),
        first_session_max_stage=int(contract["FIRST_SESSION_MAX_STAGE"]),
        anti_regression_min_lower_stage_messages=int(
            contract["ANTI_REGRESSION_MIN_LOWER_STAGE_MESSAGES"]
        ),
        stage_roles={
            int(k): v for k, v in cast(dict[int, str], contract["STAGE_ROLES"]).items()
        },
        stage_recommendations={
            int(k): v
            for k, v in cast(dict[int, str], contract["STAGE_RECOMMENDATIONS"]).items()
        },
    )



@lru_cache(maxsize=1)
def load_stage_classifier() -> StageClassifierRules:
    """Load and validate the shipped stage-classifier knowledge once per process."""
    path = default_skill_path("skills/meta/stage-classifier.md")
    return parse_stage_classifier(path.read_text(encoding="utf-8"))
