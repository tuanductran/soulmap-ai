"""Detect realizations that call for meaning integration."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

EXPLICIT_INSIGHT = [
    "i finally understand",
    "i finally see",
    "i finally realize",
    "i finally get it",
    "i finally know why",
    "i now understand",
    "i now see",
    "i now realize",
    "oh — that's",
    "oh that's why",
    "oh i see",
    "i just realized",
    "i just understood",
    "i just saw",
    "it just clicked",
    "something clicked",
    "it all makes sense",
    "i never saw it before but",
    "i never understood but now",
    "that's what's been happening",
    "that's what i've been doing",
    "i can see now that",
    "i can see clearly now",
    "i understand now",
    "i get it now",
    "i see it now",
    "this is why i",
    "that's why i always",
    "that's why i keep",
    "i've been doing this my whole",
    "i've been doing this for years",
]

EMERGING_INSIGHT = [
    "i'm starting to see",
    "i'm beginning to understand",
    "i think i see",
    "i think i understand now",
    "maybe that's why",
    "i wonder if that's why",
    "it's becoming clearer",
    "something is becoming clear",
    "i'm starting to connect",
    "i can see the connection",
    "it makes more sense now",
    "it's starting to make sense",
    "i hadn't thought of it that way",
    "i never thought of it like that",
    "that reframes everything",
    "that changes how i see",
    "i think i've been",
    "i'm realizing that i",
]

SELF_APPLICATION = [
    "that's my pattern",
    "that's the pattern",
    "i see the pattern",
    "i do this with",
    "i do this when",
    "i always do this when",
    "this is what i do",
    "this is what happens when i",
    "i recognize this",
    "i recognize that in myself",
    "that's exactly what happened",
    "i can see how i",
    "so that's where it comes from",
    "so that's why i",
    "it goes back to",
    "it comes from when",
]

POST_REFLECTION = [
    "yes that's it",
    "yes exactly",
    "that's exactly right",
    "that resonates",
    "that lands",
    "that hits different",
    "that's so true",
    "i feel that",
    "that's so accurate",
    "wow yes",
    "oh wow",
    "that's it",
    "yes that's",
    "you're right",
    "that makes so much sense",
]


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
            "Insight detected. FIRST: honor the insight with holding language — "
            "'Stay with what you just saw. What does it feel like to recognize this?' "
            "Do NOT immediately move to integration questions. "
            "Let the insight breathe. Only after the user settles: offer one integration question."
        ),
        "when_it_appears": (
            "Insight detected — user is ready to locate it in time/context. "
            "Use Question 1: 'When does this pattern usually show up for you — "
            "what kinds of situations, or what kind of day?'"
        ),
        "noticing_earlier": (
            "Insight detected — user wants to catch the pattern earlier. "
            "Use Question 2: 'What are the early signals — in your body, your mood — "
            "that this is beginning?'"
        ),
        "different_response": (
            "Insight detected — user is considering a different response. "
            "Slow this down first. Use Question 3 with care: "
            "'If you noticed this one moment earlier — not to stop it, just to see it — "
            "what might become possible in that pause?' "
            "Do NOT prescribe. Explore the space, not the action."
        ),
    }

    recommendation = (
        f"Insight moment detected (strength: {strength}, type: {insight_type}). "
        "Activate Meaning Integration Guide from skills/frameworks/meaning_integration.md. "
        + integration_map.get(insight_type, integration_map["hold_first"])
        + " End with one conscious-noticing question from "
        "skills/meta/deep_inquiry_bank.md — 'Integration-Specific Questions' section. "
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
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        history = require_list_field(data, "history")

        if not message:
            print(json.dumps({"error": "No 'message' field in input."}))
            sys.exit(1)

        result = detect_insight(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
