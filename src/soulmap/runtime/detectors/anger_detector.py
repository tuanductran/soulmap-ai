"""Detect anger signals that can activate the anger companion layer."""

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

# Single source of truth: skills/frameworks/anger-companion.md,
# "## Detection signals". Nothing is hardcoded here.
_ANGER_GROUPS = load_labeled_groups(
    runtime_skill_path("anger-companion"), "Detection signals"
)
ACTIVE_ANGER = _ANGER_GROUPS["active anger"]
SELF_ANGER = _ANGER_GROUPS["self-directed anger"]
RESIDUAL_ANGER = _ANGER_GROUPS["residual anger"]
_ANGER_SCORING = load_key_value_table(runtime_skill_path("anger-companion"), "Scoring")
_ANGER_TYPES = load_key_value_table(
    runtime_skill_path("anger-companion"), "Detection type mapping"
)
_ANGER_GUIDANCE = load_key_value_table(
    runtime_skill_path("anger-companion"), "Guidance"
)


HistoryMessage = dict[str, str]


def detect_anger(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Score anger signals in the current message.

    Matches the phrase groups authored in
    ``skills/frameworks/anger-companion.md``: active anger, self-directed
    anger, and residual anger. The first group to match sets the type, so a
    message carrying more than one reports the strongest.

    Args:
        message: The user's current message.
        history: Prior turns. Accepted for a uniform detector signature and
            not used, since anger is read from the current message.

    Returns:
        A dict with ``anger_detected``, ``anger_type``, ``score``,
        ``signals``, and ``recommendation``.
    """
    msg = message.lower().strip()
    signals = []
    score = 0
    anger_type = None

    for phrase in ACTIVE_ANGER:
        if phrase in msg:
            score += int(_ANGER_SCORING["Active anger weight"])
            signals.append(f"active: '{phrase}'")
            anger_type = _ANGER_TYPES["active anger"]
            break

    for phrase in SELF_ANGER:
        if phrase in msg:
            score += int(_ANGER_SCORING["Self-directed anger weight"])
            signals.append(f"self_anger: '{phrase}'")
            if not anger_type:
                anger_type = _ANGER_TYPES["self-directed anger"]
            break

    for phrase in RESIDUAL_ANGER:
        if phrase in msg:
            score += int(_ANGER_SCORING["Residual anger weight"])
            signals.append(f"residual: '{phrase}'")
            if not anger_type:
                anger_type = _ANGER_TYPES["residual anger"]
            break

    if history and anger_type == _ANGER_TYPES["active anger"]:
        recent = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-int(_ANGER_SCORING["Sustained history window"]) :]
        anger_count = sum(
            1
            for m in recent
            if any(
                p in m
                for p in ACTIVE_ANGER[
                    : int(_ANGER_SCORING["Sustained active-signal limit"])
                ]
            )
        )
        if anger_count >= int(_ANGER_SCORING["Sustained history threshold"]):
            score += int(_ANGER_SCORING["Sustained active anger bonus"])
            signals.append("sustained_anger_across_messages")

    if score < int(_ANGER_SCORING["Minimum detection score"]):
        return {
            "anger_detected": False,
            "anger_type": None,
            "score": score,
            "signals": [],
        }

    guidance_map = _ANGER_GUIDANCE

    return {
        "anger_detected": True,
        "anger_type": anger_type,
        "score": score,
        "signals": signals,
        "note": "Anger companion  -  meet the anger before exploring it.",
        "recommendation": guidance_map.get(anger_type or "", ""),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        result = detect_anger(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
