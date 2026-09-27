"""Load integration-celebration runtime detection knowledge from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from soulmap.runtime.knowledge.keyword_lists import (
    default_skill_path,
    load_labeled_groups,
)

_CONTRACT_HEADING = "Runtime detection contract"


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
    guidance: dict[str, str]


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


_ROW_RE = re.compile(
    r"^\|\s*(?P<setting>[^|]+?)\s*\|\s*(?P<value>[^|]*?)\s*\|\s*$", re.MULTILINE
)


def _table_rows(body: str) -> list[tuple[str, str]]:
    return [
        (match.group("setting").strip(), match.group("value").strip())
        for match in _ROW_RE.finditer(body)
        if match.group("setting").strip().lower() != "setting"
    ]


def _section_body(body: str, heading: str) -> str:
    match = re.search(rf"^### {re.escape(heading)}\s*$", body, re.MULTILINE)
    if match is None:
        raise ValueError(f"Celebration section {heading!r} is missing.")
    remainder = body[match.end() :]
    next_heading = re.search(r"^###\s+", remainder, re.MULTILINE)
    return remainder[: next_heading.start()] if next_heading else remainder


def _quoted_bullets(body: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(re.findall(r'^- "([^"]+)"\s*$', body, re.MULTILINE)))


def _literal_config(body: str) -> dict[str, object]:
    scoring = dict(_table_rows(_section_body(body, "Scoring")))
    required = {
        "Detection threshold",
        "Negative override penalty",
        "Strong-signal threshold",
        "Confirmation score",
    }
    if not required <= scoring.keys():
        raise ValueError("Celebration scoring configuration is incomplete.")
    try:
        values: dict[str, object] = {
            "SCORE_WEIGHTS": {
                key.removeprefix("Score weight: "): int(value)
                for key, value in scoring.items()
                if key.startswith("Score weight: ")
            },
            "THRESHOLD": int(scoring["Detection threshold"]),
            "NEGATIVE_OVERRIDE_PENALTY": int(scoring["Negative override penalty"]),
            "STRENGTH_THRESHOLD": int(scoring["Strong-signal threshold"]),
            "CONFIRMATION_SCORE": int(scoring["Confirmation score"]),
            "NEGATIVE_OVERRIDES": _quoted_bullets(
                _section_body(body, "Negative overrides")
            ),
            "CONFIRMATION_SIGNALS": _quoted_bullets(
                _section_body(body, "Confirmation signals")
            ),
            "CONFIRMATION_ASSISTANT_ANCHORS": _quoted_bullets(
                _section_body(body, "Confirmation assistant anchors")
            ),
        }
    except (KeyError, ValueError) as exc:
        raise ValueError("Celebration runtime configuration is invalid.") from exc
    weights = values["SCORE_WEIGHTS"]
    if (
        not isinstance(weights, dict)
        or not weights
        or any(
            not isinstance(k, str) or not isinstance(v, int) for k, v in weights.items()
        )
    ):
        raise ValueError("Celebration score weights are invalid.")
    for key in (
        "NEGATIVE_OVERRIDES",
        "CONFIRMATION_SIGNALS",
        "CONFIRMATION_ASSISTANT_ANCHORS",
    ):
        value = values[key]
        if (
            not isinstance(value, tuple)
            or not value
            or not all(isinstance(item, str) and item for item in value)
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
    guidance = load_key_value_table(path, "Guidance")
    required_guidance = {"not_detected", "detected", "closing"}
    if not required_guidance <= guidance.keys():
        raise ValueError("Celebration guidance configuration is incomplete.")
    return CelebrationRules(
        score_weights=cast(dict[str, int], values["SCORE_WEIGHTS"]),
        threshold=cast(int, values["THRESHOLD"]),
        negative_override_penalty=cast(int, values["NEGATIVE_OVERRIDE_PENALTY"]),
        strength_threshold=cast(int, values["STRENGTH_THRESHOLD"]),
        confirmation_score=cast(int, values["CONFIRMATION_SCORE"]),
        negative_overrides=cast(tuple[str, ...], values["NEGATIVE_OVERRIDES"]),
        confirmation_signals=cast(tuple[str, ...], values["CONFIRMATION_SIGNALS"]),
        confirmation_assistant_anchors=cast(
            tuple[str, ...], values["CONFIRMATION_ASSISTANT_ANCHORS"]
        ),
        signal_groups=groups,
        guidance=guidance,
    )
