"""Load stage-classification knowledge with Python-owned scoring configuration."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.runtime_config import STAGE_CLASSIFIER_CONFIG
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_STAGE_RE = re.compile(r"^### Stage (?P<number>[1-6]), (?P<name>.+?)\s*$", re.MULTILINE)
_KEYWORDS_RE = re.compile(
    r"\*\*Keyword signals:\*\*(?P<body>.*?)(?=\n\*\*Classification signals:\*\*|\Z)",
    re.DOTALL,
)
_QUOTED_RE = re.compile(r'^- "([^"]+)"\s*$', re.MULTILINE)


@dataclass(frozen=True, slots=True)
class StageRule:
    """Executable scoring rules for one user-journey stage."""

    number: int
    name: str
    weight: int
    keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StageClassifierRules:
    """Validated runtime stage rules."""

    stages: tuple[StageRule, ...]
    recent_message_window: int
    memory_session_count_threshold: int
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
    """Convert a stage heading into its public display name."""
    return raw_name.replace(" and ", " & ").title()



def _validate_stage_mapping(name: str, *, integer_values: bool) -> None:
    rows = STAGE_CLASSIFIER_CONFIG[name]
    if not isinstance(rows, list) or len(rows) != 6 or any(
        not isinstance(row, list) or len(row) != 2 for row in rows
    ):
        raise ValueError(f"Stage configuration {name!r} must contain six key/value rows.")

    stage_numbers = [row[0] for row in rows]
    if (
        any(type(number) is not int for number in stage_numbers)
        or len(set(stage_numbers)) != 6
        or set(stage_numbers) != set(range(1, 7))
    ):
        raise ValueError(f"Stage configuration {name!r} must map each stage exactly once.")

    if integer_values:
        if any(type(row[1]) is not int or row[1] < 0 for row in rows):
            raise ValueError(f"Stage configuration {name!r} values must be non-negative integers.")
    elif any(not isinstance(row[1], str) or not row[1].strip() for row in rows):
        raise ValueError(f"Stage configuration {name!r} values must be non-empty strings.")


def parse_stage_classifier(text: str) -> StageClassifierRules:
    """Parse semantic stage signals and combine them with Python-owned policy."""
    matches = list(_STAGE_RE.finditer(text))
    if len(matches) != 6:
        raise ValueError(f"Expected 6 stage definitions, found {len(matches)}.")
    stage_numbers = [int(match.group("number")) for match in matches]
    if len(set(stage_numbers)) != 6 or set(stage_numbers) != set(range(1, 7)):
        raise ValueError("Stage Markdown must define stages 1 through 6 exactly once.")

    expected_config_keys = {
        "recent_message_window",
        "memory_session_count_threshold",
        "keyword_weights",
        "thresholds",
        "recency_multipliers",
        "memory_minimums",
        "close_score_delta",
        "first_session_default_stage",
        "first_session_max_stage",
        "anti_regression_min_lower_stage_messages",
        "stage_roles",
        "stage_recommendations",
    }
    if set(STAGE_CLASSIFIER_CONFIG) != expected_config_keys:
        raise ValueError("Stage classifier configuration keys are incomplete or unused.")

    for name in ("keyword_weights", "thresholds"):
        _validate_stage_mapping(name, integer_values=True)
    for name in ("stage_roles", "stage_recommendations"):
        _validate_stage_mapping(name, integer_values=False)

    weights = dict(STAGE_CLASSIFIER_CONFIG["keyword_weights"])
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
        number = int(match.group("number"))
        if not keywords or number not in weights:
            raise ValueError(
                f"Stage {number} has incomplete semantic signals or scoring configuration."
            )
        stages.append(
            StageRule(
                number=number,
                name=_display_name(match.group("name")),
                weight=weights[number],
                keywords=keywords,
            )
        )

    for name in (
        "recent_message_window",
        "memory_session_count_threshold",
        "first_session_default_stage",
        "first_session_max_stage",
        "anti_regression_min_lower_stage_messages",
    ):
        value = STAGE_CLASSIFIER_CONFIG[name]
        if type(value) is not int or value < 1:
            raise ValueError(f"Stage configuration {name!r} must be a positive integer.")

    close_score_delta = STAGE_CLASSIFIER_CONFIG["close_score_delta"]
    if type(close_score_delta) not in (int, float) or close_score_delta < 0:
        raise ValueError("Stage close_score_delta must be a non-negative number.")

    recency_multipliers = STAGE_CLASSIFIER_CONFIG["recency_multipliers"]
    if not isinstance(recency_multipliers, list) or not recency_multipliers or any(
        type(value) not in (int, float) or value <= 0 for value in recency_multipliers
    ):
        raise ValueError("Stage recency multipliers must be positive numbers.")

    memory_minimums = STAGE_CLASSIFIER_CONFIG["memory_minimums"]
    if not isinstance(memory_minimums, dict) or not memory_minimums or any(
        not isinstance(key, str)
        or not key.strip()
        or type(value) is not int
        or value < 0
        for key, value in memory_minimums.items()
    ):
        raise ValueError("Stage memory minimums must be non-negative integer mappings.")

    if not (
        1
        <= STAGE_CLASSIFIER_CONFIG["first_session_default_stage"]
        <= STAGE_CLASSIFIER_CONFIG["first_session_max_stage"]
        <= 6
    ):
        raise ValueError("First-session stage bounds must be ordered within stages 1 through 6.")

    return StageClassifierRules(
        stages=tuple(stages),
        recent_message_window=int(STAGE_CLASSIFIER_CONFIG["recent_message_window"]),
        memory_session_count_threshold=int(
            STAGE_CLASSIFIER_CONFIG["memory_session_count_threshold"]
        ),
        thresholds=dict(STAGE_CLASSIFIER_CONFIG["thresholds"]),
        recency_multipliers=tuple(recency_multipliers),
        memory_minimums=dict(memory_minimums),
        close_score_delta=float(close_score_delta),
        first_session_default_stage=int(
            STAGE_CLASSIFIER_CONFIG["first_session_default_stage"]
        ),
        first_session_max_stage=int(STAGE_CLASSIFIER_CONFIG["first_session_max_stage"]),
        anti_regression_min_lower_stage_messages=int(
            STAGE_CLASSIFIER_CONFIG["anti_regression_min_lower_stage_messages"]
        ),
        stage_roles=dict(STAGE_CLASSIFIER_CONFIG["stage_roles"]),
        stage_recommendations=dict(STAGE_CLASSIFIER_CONFIG["stage_recommendations"]),
    )


@lru_cache(maxsize=1)
def load_stage_classifier() -> StageClassifierRules:
    """Load semantic stage signals and validated runtime policy once per process."""
    path = runtime_skill_path("stage-classifier")
    return parse_stage_classifier(path.read_text(encoding="utf-8"))
