"""Detect positive emotional states that call for the Integration and Celebration framework (P9b)."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from soulmap.runtime.knowledge.celebration_source import load_celebration_rules

_RULES = load_celebration_rules()

HistoryMessage = dict[str, str]

def _classify_celebration_type(msg: str) -> str:
    """Identify the primary subtype of the positive state."""
    groups = _RULES.signal_groups
    if any(p in msg for p in groups["recognized progress"]):
        return "recognized_progress"
    if any(p in msg for p in groups["win or completion"]):
        return "win"
    if any(p in msg for p in groups["relief after difficulty"]):
        return "relief"
    if any(p in msg for p in groups["gratitude"]):
        return "gratitude"
    return "general_positive"


def detect_celebration(
    message: str,
    history: list[HistoryMessage] | None = None,
) -> dict[str, object]:
    """Score positive primary states that call for the celebration framework.

    Detects a win, relief, gratitude, or recognized progress as the message's
    primary state, which routes to Integration and Celebration. A negative
    signal in the same message sets the override flag, since a positive phrase
    wrapped around real distress is not a celebration.

    Args:
        message: The user's current message.
        history: Prior turns, each a dict with ``role`` and ``content``.

    Returns:
        A dict with ``celebration_detected``, ``strength``,
        ``celebration_type``, ``score``, ``signals``,
        ``has_negative_override``, and ``recommendation``.
    """
    msg = message.lower().strip()
    signals_found: list[str] = []
    score = 0

    for phrase in _RULES.signal_groups["win or completion"]:
        if phrase in msg:
            score += _RULES.score_weights["win or completion"]
            signals_found.append(f"win: '{phrase}'")
            break  # one win signal is enough to score the category

    for phrase in _RULES.signal_groups["relief after difficulty"]:
        if phrase in msg:
            score += _RULES.score_weights["relief after difficulty"]
            signals_found.append(f"relief: '{phrase}'")
            break

    for phrase in _RULES.signal_groups["gratitude"]:
        if phrase in msg:
            score += _RULES.score_weights["gratitude"]
            signals_found.append(f"gratitude: '{phrase}'")
            break

    for phrase in _RULES.signal_groups["recognized progress"]:
        if phrase in msg:
            score += _RULES.score_weights["recognized progress"]
            signals_found.append(f"progress: '{phrase}'")
            break

    # Check for negative override - mixed pain signals reduce confidence
    has_negative_override = any(neg in msg for neg in _RULES.negative_overrides)

    if has_negative_override:
        score = max(0, score - _RULES.negative_override_penalty)
        signals_found.append("negative_override: mixed pain signal detected")

    # Check prior assistant turn for a reflection that user is now confirming positively
    if history:
        recent_assistant = [
            m["content"].lower()
            for m in history[-2:]
            if isinstance(m, dict) and m.get("role") == "assistant"
        ]
        if any(conf in msg for conf in _RULES.confirmation_signals) and any(
            any(sig in am for sig in _RULES.confirmation_assistant_anchors)
            for am in recent_assistant
        ):
            score += _RULES.confirmation_score
            signals_found.append("confirms_celebration_reflection")

    if score < _RULES.threshold:
        return {
            "celebration_detected": False,
            "strength": None,
            "celebration_type": None,
            "score": score,
            "signals": signals_found,
            "has_negative_override": has_negative_override,
            "recommendation": (
                "No celebration signal detected. Continue standard pipeline."
            ),
        }

    strength = "strong" if score >= _RULES.strength_threshold else "present"
    celebration_type = _classify_celebration_type(msg)

    recommendation = (
        f"Celebration signal detected (strength: {strength}, "
        f"type: {celebration_type}). "
        "Activate integration-celebration.md (P9b). "
        "Use the framework's four-step arc and the type-specific guidance already "
        "defined in the Markdown source. Do NOT perform enthusiasm. "
        "Do NOT open with exclamation. Do NOT immediately ask 'what is next'. "
        "Close with one agency-preserving question from deep-inquiry-bank.md. "
        "Closing ritual: skills/voice/session-rituals.md "
        "(Breakthrough and Celebration Closing section)."
    )

    return {
        "celebration_detected": True,
        "strength": strength,
        "celebration_type": celebration_type,
        "score": score,
        "signals": signals_found,
        "has_negative_override": has_negative_override,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_celebration(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
