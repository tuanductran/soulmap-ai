"""Detect repeated external frustrations that may point to shadow work."""

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
    load_keyword_section,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/shadow-patterns/content/shadow-patterns.md and
# skills/frameworks/self-compassion.md. Nothing is hardcoded here — every
# phrase list is parsed straight from those Markdown skills.
_SHADOW_PATH = runtime_skill_path("shadow-patterns")
_SELF_COMPASSION_PATH = runtime_skill_path("self-compassion")

EXTERNAL_REPEAT_SIGNALS = load_keyword_section(
    _SHADOW_PATH, "External frustration signals"
)
AVOIDANCE_SIGNALS = load_keyword_section(_SHADOW_PATH, "Avoidance (as protection)")
PEOPLE_PLEASING_SIGNALS = load_keyword_section(
    _SHADOW_PATH, "People Pleasing (as protection)"
)
OVERTHINKING_SIGNALS = load_keyword_section(
    _SHADOW_PATH, "Overthinking Instead of Feeling (as protection)"
)
WITHDRAWAL_SIGNALS = load_keyword_section(
    _SHADOW_PATH, "Emotional Withdrawal (as protection)"
)
PERFECTIONISM_SIGNALS = load_keyword_section(
    _SHADOW_PATH, "Perfectionism (as protection)"
)
SELF_CRITIC_SIGNALS = load_keyword_section(_SELF_COMPASSION_PATH, "Detection signals")
_SHADOW_SCORING = load_key_value_table(_SHADOW_PATH, "Scoring")
_SHADOW_GUIDANCE = load_key_value_table(_SHADOW_PATH, "Guidance")


HistoryMessage = dict[str, str]


def detect_shadow_patterns(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect shadow pattern signals in the current message and recent history.

    Returns:
        Dict with: shadow_detected (bool), patterns_found (list),
                   is_external_frustration (bool), recommendation (str)
    """
    msg = message.lower().strip()
    patterns_found = []
    external_frustration = False
    score = 0

    for phrase in EXTERNAL_REPEAT_SIGNALS:
        if phrase in msg:
            score += int(_SHADOW_SCORING["External-repeat weight"])
            external_frustration = True
            break

    pattern_checks = [
        ("avoidance", AVOIDANCE_SIGNALS, int(_SHADOW_SCORING["Avoidance weight"])),
        (
            "people_pleasing",
            PEOPLE_PLEASING_SIGNALS,
            int(_SHADOW_SCORING["People-pleasing weight"]),
        ),
        (
            "overthinking",
            OVERTHINKING_SIGNALS,
            int(_SHADOW_SCORING["Overthinking weight"]),
        ),
        ("withdrawal", WITHDRAWAL_SIGNALS, int(_SHADOW_SCORING["Withdrawal weight"])),
        (
            "perfectionism",
            PERFECTIONISM_SIGNALS,
            int(_SHADOW_SCORING["Perfectionism weight"]),
        ),
    ]

    for pattern_name, signals, weight in pattern_checks:
        for phrase in signals:
            if phrase in msg:
                score += weight
                patterns_found.append(pattern_name)
                break  # one match per pattern

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-int(_SHADOW_SCORING["Recent user history window"]) :]

        external_count = sum(
            1
            for past in recent_user
            if any(
                phrase in past
                for phrase in EXTERNAL_REPEAT_SIGNALS[
                    : int(_SHADOW_SCORING["Sustained external-signal limit"])
                ]
            )
        )
        if external_count >= int(_SHADOW_SCORING["Sustained history threshold"]):
            score += int(_SHADOW_SCORING["Sustained external-frustration bonus"])
            external_frustration = True

    if score < int(_SHADOW_SCORING["Minimum detection score"]):
        return {
            "shadow_detected": False,
            "patterns_found": [],
            "is_external_frustration": external_frustration,
            "score": score,
            "recommendation": "No shadow pattern signals detected. Continue standard pipeline.",
        }

    # Self-criticism alone must not be enough to trigger shadow detection:
    # self-compassion.md's own doctrine says a standalone self-attack routes
    # via default Mirror, not Shadow. It only enriches an already-triggered
    # shadow result (another pattern, or repeated external frustration,
    # already crossed the score threshold above).
    for phrase in SELF_CRITIC_SIGNALS:
        if phrase in msg:
            score += int(_SHADOW_SCORING["Self-criticism enrichment bonus"])
            patterns_found.append("self_criticism")
            break

    if patterns_found:
        recommendation = _SHADOW_GUIDANCE["pattern"]
    elif external_frustration:
        recommendation = _SHADOW_GUIDANCE["external_frustration"]
    else:
        recommendation = _SHADOW_GUIDANCE["mild"]

    return {
        "shadow_detected": True,
        "patterns_found": patterns_found,
        "is_external_frustration": external_frustration,
        "score": score,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_shadow_patterns(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
