"""Detect life-direction lostness and values-level misalignment."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.config import (
    COMPARISON_SIGNALS,
    LOSTNESS_SIGNALS,
    MEANING_SIGNALS,
    MISALIGNMENT_SIGNALS,
    SHOULD_SIGNALS,
    TRANSITION_SIGNALS,
)
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]


def _suggest_lens(msg: str) -> str:
    """Suggest which of the four inquiry lenses is most relevant."""
    if any(s in msg for s in MEANING_SIGNALS[:6]):
        return "Lens 1 (meaning)  -  ask about what has felt meaningful, even in small ways"
    if any(
        s in msg
        for s in ["drain", "exhaust", "energiz", "alive", "resist", "putting off"]
    ):
        return "Lens 2 (energy)  -  ask about what energizes vs. drains"
    if any(s in msg for s in SHOULD_SIGNALS[:4] + COMPARISON_SIGNALS[:4]):
        return "Lens 3 (respect)  -  ask what kind of life they would genuinely admire"
    if any(s in msg for s in MISALIGNMENT_SIGNALS[:6]):
        return "Lens 4 (misalignment)  -  help locate the gap between values and current life"
    return "Lens 1 (meaning)  -  start with what feels meaningful as the opening lens"


def detect_direction_need(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect whether the user needs the Life Direction Clarifier framework.

    Returns:
        Dict with: direction_detected (bool), type (str), score (int),
                   signals (list), suggested_lens (str), presentation (str),
                   recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    direction_types = []

    signal_groups = [
        ("lostness", LOSTNESS_SIGNALS, 3),
        ("meaning_void", MEANING_SIGNALS, 3),
        ("should_vs_want", SHOULD_SIGNALS, 2),
        ("comparison", COMPARISON_SIGNALS, 2),
        ("transition", TRANSITION_SIGNALS, 2),
        ("misalignment", MISALIGNMENT_SIGNALS, 2),
    ]

    for type_name, signals, weight in signal_groups:
        for phrase in signals:
            if phrase in msg:
                score += weight
                signals_found.append(f"{type_name}: '{phrase}'")
                if type_name not in direction_types:
                    direction_types.append(type_name)
                break  # one match per group per pass is enough

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-4:]
        history_signals = (
            LOSTNESS_SIGNALS[:8] + MEANING_SIGNALS[:6] + TRANSITION_SIGNALS[:6]
        )
        for past_msg in recent_user:
            if any(phrase in past_msg for phrase in history_signals):
                score += 1
                if "sustained" not in direction_types:
                    direction_types.append("sustained")
                break

    if score < 2:
        return {
            "direction_detected": False,
            "type": None,
            "score": score,
            "signals": signals_found,
            "suggested_lens": None,
            "presentation": None,
            "recommendation": "No direction signals detected. Continue standard pipeline.",
        }

    presentation_map = {
        "lostness": "lost",
        "meaning_void": "meaning_void",
        "should_vs_want": "should_vs_want",
        "comparison": "comparison",
        "transition": "transition",
        "misalignment": "misalignment",
    }
    primary_type = direction_types[0] if direction_types else "lostness"
    presentation = presentation_map.get(primary_type, "lost")

    suggested_lens = _suggest_lens(msg)

    recommendation = (
        f"Life direction uncertainty detected (type: {primary_type}). "
        "Activate Life Direction Clarifier from skills/frameworks/life-direction.md. "
        "Explore VALUES, not options. Do NOT suggest a direction or validate a leaning. "
        f"Start with: {suggested_lens}. "
        "Use one lens at a time. Follow the user's energy. "
        "End with one reflective question about what kind of life feels honest to them. "
        "Retrieve question from skills/meta/deep-inquiry-bank.md  -  'Direction-Specific Questions' section."
    )

    return {
        "direction_detected": True,
        "type": primary_type,
        "score": score,
        "signals": signals_found,
        "suggested_lens": suggested_lens,
        "presentation": presentation,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_direction_need(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
