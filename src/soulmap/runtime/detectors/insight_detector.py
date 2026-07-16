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
    default_skill_path,
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/meaning-integration.md,
# "## Detection signals". Nothing is hardcoded here.
_INSIGHT_GROUPS = load_labeled_groups(
    default_skill_path("skills/frameworks/meaning-integration.md"),
    "Detection signals",
)
EXPLICIT_INSIGHT = _INSIGHT_GROUPS["explicit insight"]
EMERGING_INSIGHT = _INSIGHT_GROUPS["emerging insight"]
SELF_APPLICATION = _INSIGHT_GROUPS["self-application"]
POST_REFLECTION = _INSIGHT_GROUPS["post-reflection validation"]

HistoryMessage = dict[str, str]


def _classify_insight_type(msg: str) -> str:
    """Determine which integration question is most appropriate."""
    when_signals = [
        "when does",
        "when do i",
        "where does",
        "where do i",
        "what situations",
        "what triggers",
        "always happens when",
    ]
    earlier_signals = [
        "catch it",
        "notice it earlier",
        "earlier",
        "before it",
        "before i",
        "sooner",
        "at the beginning",
        "the start of it",
    ]
    different_signals = [
        "what would i do",
        "what could i do",
        "different response",
        "respond differently",
        "handle it",
        "next time",
    ]

    if any(s in msg for s in earlier_signals):
        return "noticing_earlier"
    if any(s in msg for s in when_signals):
        return "when_it_appears"
    if any(s in msg for s in different_signals):
        return "different_response"
    return "hold_first"  # Default: let the insight breathe before anything else


def detect_insight(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect whether the user has reached a moment of insight or realization
    that calls for the Meaning Integration framework.

    Returns:
        Dict with: insight_detected (bool), strength (str), insight_type (str),
                   signals (list), recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0

    for phrase in EXPLICIT_INSIGHT:
        if phrase in msg:
            score += 3
            signals_found.append(f"explicit: '{phrase}'")

    for phrase in EMERGING_INSIGHT:
        if phrase in msg:
            score += 2
            signals_found.append(f"emerging: '{phrase}'")

    for phrase in SELF_APPLICATION:
        if phrase in msg:
            score += 2
            signals_found.append(f"self_application: '{phrase}'")

    for phrase in POST_REFLECTION:
        if phrase in msg:
            score += 2
            signals_found.append(f"post_reflection: '{phrase}'")

    if history:
        recent_assistant = [
            m["content"].lower()
            for m in history[-3:]
            if isinstance(m, dict) and m.get("role") == "assistant"
        ]
        integration_triggers = [
            "pattern that may appear",
            "part of you that",
            "sometimes when",
            "i wonder if",
        ]
        if any(any(t in am for t in integration_triggers) for am in recent_assistant):
            validation = [
                "yes",
                "exactly",
                "resonates",
                "right",
                "true",
                "that's it",
                "that fits",
                "spot on",
            ]
            if any(v in msg for v in validation) and len(msg.split()) < 30:
                score += 3
                signals_found.append("validation_of_reflection")

    if score < 2:
        return {
            "insight_detected": False,
            "strength": None,
            "insight_type": None,
            "score": score,
            "signals": signals_found,
            "recommendation": "No insight signal detected. Continue standard response pipeline.",
        }

    strength = "strong" if score >= 4 else "emerging"
    insight_type = _classify_insight_type(msg)

    integration_map = {
        "hold_first": (
            "Insight detected. FIRST: honor the insight with holding language  -  "
            "'Stay with what you just saw. What does it feel like to recognize this?' "
            "Do NOT immediately move to integration questions. "
            "Let the insight breathe. Only after the user settles: offer one integration question."
        ),
        "when_it_appears": (
            "Insight detected  -  user is ready to locate it in time/context. "
            "Use Question 1: 'When does this pattern usually show up for you  -  "
            "what kinds of situations, or what kind of day?'"
        ),
        "noticing_earlier": (
            "Insight detected  -  user wants to catch the pattern earlier. "
            "Use Question 2: 'What are the early signals  -  in your body, your mood  -  "
            "that this is beginning?'"
        ),
        "different_response": (
            "Insight detected  -  user is considering a different response. "
            "Slow this down first. Use Question 3 with care: "
            "'If you noticed this one moment earlier  -  not to stop it, just to see it  -  "
            "what might become possible in that pause?' "
            "Do NOT prescribe. Explore the space, not the action."
        ),
    }

    recommendation = (
        f"Insight moment detected (strength: {strength}, type: {insight_type}). "
        "Activate Meaning Integration Guide from skills/frameworks/meaning-integration.md. "
        + integration_map.get(insight_type, integration_map["hold_first"])
        + " End with one conscious-noticing question from "
        "skills/meta/deep-inquiry-bank.md  -  'Integration-Specific Questions' section. "
        "Do NOT prescribe change. Focus on awareness. Do not use the word 'should'."
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
