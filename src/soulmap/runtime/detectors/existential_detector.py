"""Detect existential territory that needs holding rather than solving."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from soulmap.runtime.knowledge.keyword_lists import (
    load_key_value_table,
    load_labeled_groups,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/existential-companion/content/existential-companion.md,
# "## Detection signals". Nothing is hardcoded here.
_EXISTENTIAL_GROUPS = load_labeled_groups(
    runtime_skill_path("existential-companion"),
    "Detection signals",
)
_EXISTENTIAL_TERRITORIES = load_key_value_table(
    runtime_skill_path("existential-companion"), "Detection territory groups"
)
_EXISTENTIAL_SCORING = load_key_value_table(
    runtime_skill_path("existential-companion"), "Scoring"
)
_EXISTENTIAL_GUIDANCE = load_key_value_table(
    runtime_skill_path("existential-companion"), "Guidance"
)


HistoryMessage = dict[str, str]


def _classify_territory(_msg: str, scores: dict[str, int]) -> str:
    """Return the primary existential territory."""
    territory_scores = {
        territory: scores.get(territory, 0)
        for territory in _EXISTENTIAL_TERRITORIES.values()
    }
    primary = max(territory_scores, key=lambda territory: territory_scores[territory])
    if territory_scores[primary] == 0:
        return "general"
    return primary


def detect_existential(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect existential territory in the user's message.

    Returns:
        Dict with: existential_detected (bool), territory (str), score (int),
                   signals (list), recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    territory_scores = dict.fromkeys(_EXISTENTIAL_TERRITORIES.values(), 0)

    signal_sources = {
        territory: _EXISTENTIAL_GROUPS[group]
        for group, territory in _EXISTENTIAL_TERRITORIES.items()
    }
    signal_weights = {
        territory: int(_EXISTENTIAL_SCORING[f"{territory} weight"])
        for territory in _EXISTENTIAL_TERRITORIES.values()
    }
    signal_map = [
        (name, signal_sources[name], signal_weights[name])
        for name in (
            item.strip()
            for item in _EXISTENTIAL_SCORING["Territory priority"].split(";")
            if item.strip()
        )
    ]

    for territory, signals, weight in signal_map:
        for phrase in signals:
            if phrase in msg:
                score += weight
                territory_scores[territory] += weight
                signals_found.append(f"{territory}: '{phrase}'")
                break  # one match per territory per pass

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-int(_EXISTENTIAL_SCORING["Recent user history window"]) :]
        returning_signals = [
            phrase
            for territory in _EXISTENTIAL_TERRITORIES.values()
            if territory != "holding"
            for phrase in signal_sources[territory][
                : int(_EXISTENTIAL_SCORING[f"Sustained {territory} signal limit"])
            ]
        ]
        count = sum(
            1
            for past in recent_user
            if any(phrase in past for phrase in returning_signals)
        )
        if count >= int(_EXISTENTIAL_SCORING["Sustained history threshold"]):
            score += int(_EXISTENTIAL_SCORING["Sustained-territory bonus"])
            signals_found.append(
                "sustained: existential territory across multiple messages"
            )

    if score < int(_EXISTENTIAL_SCORING["Minimum detection score"]):
        return {
            "existential_detected": False,
            "territory": None,
            "score": score,
            "signals": signals_found,
            "recommendation": "No existential signals detected. Continue standard pipeline.",
        }

    territory = _classify_territory(msg, territory_scores)

    territory_guidance = _EXISTENTIAL_GUIDANCE.get(
        territory, _EXISTENTIAL_GUIDANCE["general"]
    )
    recommendation = (
        _EXISTENTIAL_GUIDANCE["detected_prefix"].format(
            territory=territory, guidance=territory_guidance
        )
        + " "
        + _EXISTENTIAL_GUIDANCE["detected_suffix"]
    )

    return {
        "existential_detected": True,
        "territory": territory,
        "score": score,
        "signals": signals_found,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_existential(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
