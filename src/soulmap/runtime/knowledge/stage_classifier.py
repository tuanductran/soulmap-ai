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


def parse_stage_classifier(text: str) -> StageClassifierRules:
    """Parse semantic stage signals and combine them with Python-owned policy."""
    matches = list(_STAGE_RE.finditer(text))
    if len(matches) != 6:
        raise ValueError(f"Expected 6 stage definitions, found {len(matches)}.")

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

    return StageClassifierRules(
        stages=tuple(stages),
        thresholds=dict(STAGE_CLASSIFIER_CONFIG["thresholds"]),
        recency_multipliers=tuple(STAGE_CLASSIFIER_CONFIG["recency_multipliers"]),
        memory_minimums=dict(STAGE_CLASSIFIER_CONFIG["memory_minimums"]),
        close_score_delta=float(STAGE_CLASSIFIER_CONFIG["close_score_delta"]),
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
