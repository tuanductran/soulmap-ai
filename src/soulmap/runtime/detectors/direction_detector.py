"""Detect life-direction lostness and values-level misalignment."""

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

_SOURCE = runtime_skill_path("life-direction")
_DIRECTION_GROUPS = load_labeled_groups(_SOURCE, "Detection signals")
_DIRECTION_RULES = load_key_value_table(_SOURCE, "Scoring")
_DIRECTION_LENS_SIGNALS = load_key_value_table(_SOURCE, "Lens signals")
_DIRECTION_LENS = load_key_value_table(_SOURCE, "Lens routing")
_DIRECTION_GUIDANCE = load_key_value_table(_SOURCE, "Runtime guidance")

LOSTNESS_SIGNALS = _DIRECTION_GROUPS["lostness"]
SHOULD_SIGNALS = _DIRECTION_GROUPS["should vs. want"]
MISALIGNMENT_SIGNALS = _DIRECTION_GROUPS["misalignment"]
COMPARISON_SIGNALS = _DIRECTION_GROUPS["comparison and falling behind"]
MEANING_SIGNALS = _DIRECTION_GROUPS["meaning"]
TRANSITION_SIGNALS = _DIRECTION_GROUPS["transition"]
ENERGY_SIGNALS = _DIRECTION_GROUPS["energy"]


HistoryMessage = dict[str, str]


def _suggest_lens(msg: str) -> str:
    """Suggest the knowledge-authored inquiry lens."""
    signal_map = {
        "meaning": MEANING_SIGNALS,
        "energy": ENERGY_SIGNALS,
        "should_vs_want": SHOULD_SIGNALS,
        "comparison": COMPARISON_SIGNALS,
        "misalignment": MISALIGNMENT_SIGNALS,
    }
    for lens, groups in _DIRECTION_LENS_SIGNALS.items():
        if lens == "default":
            continue
        signals = []
        for group in groups.split(","):
            signals.extend(signal_map.get(group.strip(), ()))
        if any(signal in msg for signal in signals):
            return _DIRECTION_LENS[lens]
    return _DIRECTION_LENS["default"]


def detect_direction_need(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect whether the user needs the Life Direction Clarifier framework.

    Returns:
        Dict with: direction_detected (bool), type (str), score (int),
                   signals (list), suggested_lens (str), presentation (str),
                   recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    direction_types = []

    signal_groups = (
        ("lostness", LOSTNESS_SIGNALS),
        ("meaning_void", MEANING_SIGNALS),
        ("should_vs_want", SHOULD_SIGNALS),
        ("comparison", COMPARISON_SIGNALS),
        ("transition", TRANSITION_SIGNALS),
        ("misalignment", MISALIGNMENT_SIGNALS),
    )

    for type_name, signals in signal_groups:
        for phrase in signals:
            if phrase in msg:
                score += int(_DIRECTION_RULES[type_name])
                signals_found.append(f"{type_name}: '{phrase}'")
                if type_name not in direction_types:
                    direction_types.append(type_name)
                break  # one match per group per pass is enough

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-int(_DIRECTION_RULES["recent user history window"]) :]
        history_signals = (
            LOSTNESS_SIGNALS[: int(_DIRECTION_RULES["sustained lostness signal limit"])]
            + MEANING_SIGNALS[: int(_DIRECTION_RULES["sustained meaning signal limit"])]
            + TRANSITION_SIGNALS[
                : int(_DIRECTION_RULES["sustained transition signal limit"])
            ]
        )
        for past_msg in recent_user:
            if any(phrase in past_msg for phrase in history_signals):
                score += int(_DIRECTION_RULES["sustained history match"])
                if "sustained" not in direction_types:
                    direction_types.append("sustained")
                break

    if score < int(_DIRECTION_RULES["minimum detection score"]):
        return {
            "direction_detected": False,
            "type": None,
            "score": score,
            "signals": signals_found,
            "suggested_lens": None,
            "presentation": None,
            "recommendation": _DIRECTION_GUIDANCE["not_detected"],
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

    recommendation = _DIRECTION_GUIDANCE["detected"]

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
