"""Load the operational stage-classification rules from shipped Markdown.

The stage detector must execute the scoring algorithm authored in
``skills/meta/stage-classifier.md`` rather than carrying a second copy of its
keyword sets, weights, thresholds, or recency multipliers in Python.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_STAGE_RE = re.compile(
    r"^### Stage (?P<number>[1-6]), (?P<name>.+?)\s*$", re.MULTILINE
)
_KEYWORDS_RE = re.compile(
    r"\*\*Keyword signals \(weight: (?P<weight>\d+) each\):\*\*"
    r"(?P<body>.*?)(?=\n\*\*Classification signals:\*\*|\Z)",
    re.DOTALL,
)
_QUOTED_RE = re.compile(r'^- "([^"]+)"\s*$', re.MULTILINE)
_THRESHOLD_RE = re.compile(
    r"^\|\s*(?P<stage>[1-6])\s*\|\s*(?P<threshold>\d+)\s*\|",
    re.MULTILINE,
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


def _display_name(raw_name: str) -> str:
    """Convert the Markdown stage heading into the public display name."""
    return raw_name.replace(" and ", " & ").title()


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
    )


@lru_cache(maxsize=1)
def load_stage_classifier() -> StageClassifierRules:
    """Load and validate the shipped stage-classifier knowledge once per process."""
    path = default_skill_path("skills/meta/stage-classifier.md")
    return parse_stage_classifier(path.read_text(encoding="utf-8"))
