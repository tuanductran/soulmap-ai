"""Detect realizations that call for meaning integration."""

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

# Single source of truth: skills/frameworks/meaning-integration.md,
# "## Detection signals". Nothing is hardcoded here.
_INSIGHT_GROUPS = load_labeled_groups(
    runtime_skill_path("meaning-integration"),
    "Detection signals",
)
EXPLICIT_INSIGHT = _INSIGHT_GROUPS["explicit insight"]
EMERGING_INSIGHT = _INSIGHT_GROUPS["emerging insight"]
SELF_APPLICATION = _INSIGHT_GROUPS["self-application"]
POST_REFLECTION = _INSIGHT_GROUPS["post-reflection validation"]
_INSIGHT_SCORING = load_key_value_table(
    runtime_skill_path("meaning-integration"), "Scoring"
)
_INSIGHT_CLASSIFICATION = load_key_value_table(
    runtime_skill_path("meaning-integration"),
    "Insight classification signals",
)
_INSIGHT_VALIDATION = load_key_value_table(
    runtime_skill_path("meaning-integration"),
    "Reflection-validation signals",
)
_INSIGHT_GUIDANCE = load_key_value_table(
    runtime_skill_path("meaning-integration"), "Guidance"
)


def _phrases(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(";") if part.strip())


def _score(name: str) -> int:
    return int(_INSIGHT_SCORING[name])


HistoryMessage = dict[str, str]


def _classify_insight_type(msg: str) -> str:
    """Determine the integration question type from knowledge-authored signals."""
    for insight_type in _INSIGHT_SCORING["Classification priority"].split(";"):
        key = insight_type.strip()
        if any(signal in msg for signal in _phrases(_INSIGHT_CLASSIFICATION[key])):
            return key
    return _INSIGHT_SCORING["Default classification"]


def detect_insight(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Score signals that the user has reached a moment of realization.

    A genuine insight routes to the Meaning Integration framework, whose job
    is to return authorship of the insight to the user rather than to build on
    it.

    Args:
        message: The user's current message.
        history: Prior turns, each a dict with ``role`` and ``content``.

    Returns:
        A dict with ``insight_detected``, ``strength``, ``insight_type``,
        ``signals``, and ``recommendation``.
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0

    for phrase in EXPLICIT_INSIGHT:
        if phrase in msg:
            score += _score("Explicit insight weight")
            signals_found.append(f"explicit: '{phrase}'")

    for phrase in EMERGING_INSIGHT:
        if phrase in msg:
            score += _score("Emerging insight weight")
            signals_found.append(f"emerging: '{phrase}'")

    for phrase in SELF_APPLICATION:
        if phrase in msg:
            score += _score("Self-application weight")
            signals_found.append(f"self_application: '{phrase}'")

    for phrase in POST_REFLECTION:
        if phrase in msg:
            score += _score("Post-reflection validation weight")
            signals_found.append(f"post_reflection: '{phrase}'")

    if history:
        recent_assistant = [
            m["content"].lower()
            for m in history[-int(_score("Validation history window")) :]
            if isinstance(m, dict) and m.get("role") == "assistant"
        ]
        integration_triggers = _phrases(
            _INSIGHT_VALIDATION["Assistant integration triggers"]
        )
        if any(any(t in am for t in integration_triggers) for am in recent_assistant):
            validation = _phrases(_INSIGHT_VALIDATION["User validation"])
            if any(v in msg for v in validation) and len(msg.split()) < _score(
                "Validation maximum user word count"
            ):
                score += _score("Validation-of-reflection bonus")
                signals_found.append("validation_of_reflection")

    if score < _score("Minimum detection score"):
        return {
            "insight_detected": False,
            "strength": None,
            "insight_type": None,
            "score": score,
            "signals": signals_found,
            "recommendation": "No insight signal detected. Continue standard response pipeline.",
        }

    strength = (
        "strong" if score >= _score("Strong insight minimum score") else "emerging"
    )
    insight_type = _classify_insight_type(msg)

    integration_guidance = _INSIGHT_GUIDANCE.get(
        insight_type, _INSIGHT_GUIDANCE["hold_first"]
    )
    recommendation = (
        _INSIGHT_GUIDANCE["detected_prefix"].format(
            strength=strength,
            insight_type=insight_type,
            guidance=integration_guidance,
        )
        + " "
        + _INSIGHT_GUIDANCE["detected_suffix"]
    )

    return {
        "insight_detected": True,
        "strength": strength,
        "insight_type": insight_type,
        "score": score,
        "signals": signals_found,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_insight(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
