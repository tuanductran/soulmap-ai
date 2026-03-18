"""Detect inner conflict and likely competing parts in user language."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

EXPLICIT_CONFLICT = [
    "part of me wants",
    "part of me knows",
    "part of me thinks",
    "part of me feels",
    "part of me is",
    "part of me says",
    "part of me hopes",
    "part of me believes",
    "part of me needs",
    "but another part",
    "but part of me",
    "but then part of me",
    "one part of me",
    "one side of me",
    "one voice says",
    "i want to but i",
    "i want to but part",
    "i know i should but",
    "i know i shouldn't but",
    "i keep telling myself but",
    "i tell myself but then",
    "my head says",
    "my heart says",
    "my gut says",
    "i want to stay but",
    "i want to leave but",
    "i want to try but",
    "i want to stop but",
]

SELF_DIALOGUE = [
    "i keep telling myself",
    "i tell myself",
    "i say to myself",
    "i remind myself",
    "i know better but",
    "i know this but",
    "i fight with myself",
    "i argue with myself",
    "i'm at war with myself",
    "i'm fighting myself",
    "torn between",
    "i'm torn",
    "can't decide",
    "going back and forth",
    "pulled in two directions",
    "don't know which part to listen to",
    "don't know which voice",
]

PART_NAMING = [
    "a part of me",
    "that part of me",
    "this part of me",
    "the part that",
    "the part of me that",
    "a side of me",
    "the side that",
    "a voice in me",
    "a voice that says",
    "something in me says",
    "something in me wants",
    "something in me won't",
    "something in me keeps",
]

BEHAVIORAL_CONFUSION = [
    "i don't understand why i",
    "don't know why i did",
    "i surprised myself",
    "i don't recognize myself",
    "that's not like me",
    "i acted against my own values",
    "i did the opposite of what i wanted",
    "i don't know what i want",
    "i'm confusing myself",
    "i contradict myself",
    "i'm exhausted from fighting myself",
    "tired of fighting myself",
    "at war with myself",
    "battling myself",
]


def detect_inner_conflict(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect inner conflict signals in the current message and recent history.

    Args:
        message: The current user message.
        history: Full conversation history (optional).

    Returns:
        Dict with: conflict_detected (bool), type (str), signals (list),
                   parts_suggested (list), recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    conflict_types = []

    for phrase in EXPLICIT_CONFLICT:
        if phrase in msg:
            score += 3
            signals_found.append(f"explicit: '{phrase}'")
            if "explicit" not in conflict_types:
                conflict_types.append("explicit")

    for phrase in SELF_DIALOGUE:
        if phrase in msg:
            score += 2
            signals_found.append(f"self_dialogue: '{phrase}'")
            if "self_dialogue" not in conflict_types:
                conflict_types.append("self_dialogue")

    for phrase in PART_NAMING:
        if phrase in msg:
            score += 2
            signals_found.append(f"part_naming: '{phrase}'")
            if "part_naming" not in conflict_types:
                conflict_types.append("part_naming")

    for phrase in BEHAVIORAL_CONFUSION:
        if phrase in msg:
            score += 2
            signals_found.append(f"confusion: '{phrase}'")
            if "behavioral_confusion" not in conflict_types:
                conflict_types.append("behavioral_confusion")

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-3:]
        for past_msg in recent_user:
            for phrase in EXPLICIT_CONFLICT[:8]:  # Check strongest signals in history
                if phrase in past_msg:
                    score += 1
                    if "historical" not in conflict_types:
                        conflict_types.append("historical")
                    break

    parts_suggested = _suggest_parts(msg)

    conflict_detected = score >= 2

    if not conflict_detected:
        return {
            "conflict_detected": False,
            "type": None,
            "score": score,
            "signals": signals_found,
            "parts_suggested": [],
            "recommendation": (
                "No inner conflict signals detected. "
                "Continue standard response pipeline."
            ),
        }

    primary_type = conflict_types[0] if conflict_types else "general"

    recommendation = (
        f"Inner conflict detected ({primary_type}). "
        "Activate Inner Parts framework from skills/frameworks/inner_parts.md. "
        "Name 1-2 parts visible in the message. "
        "Reflect the hidden intention behind each part. "
        "Do NOT take sides. Do NOT attempt to resolve the conflict. "
        "End with one question that invites the user to listen to one of the parts. "
        "Use post-grounding questions from skills/meta/deep_inquiry_bank.md — 'Parts-Specific Questions' section."
    )

    if parts_suggested:
        recommendation += (
            f" Likely parts present: {', '.join(parts_suggested)}. "
            "Use reflection language from the relevant part sections in skills/frameworks/inner_parts.md."
        )

    return {
        "conflict_detected": True,
        "type": primary_type,
        "score": score,
        "signals": signals_found,
        "parts_suggested": parts_suggested,
        "recommendation": recommendation,
    }


def _suggest_parts(msg: str) -> list[str]:
    """
    Suggest which part archetypes are likely visible in the message.
    Based on keyword proximity to part signals.
    """
    suggestions = []

    protective_signals = [
        "wall",
        "guard",
        "let in",
        "shut down",
        "closed off",
        "protect",
        "don't need",
        "independent",
        "rely on no one",
        "keep distance",
    ]
    fearful_signals = [
        "what if",
        "worst case",
        "something goes wrong",
        "afraid",
        "scared",
        "imagining",
        "waiting for it to",
        "fall apart",
        "won't last",
    ]
    hopeful_signals = [
        "still believe",
        "maybe",
        "could be different",
        "haven't given up",
        "still hoping",
        "still think",
        "somewhere in me",
        "trying again",
    ]
    tired_signals = [
        "exhausted",
        "tired of",
        "can't anymore",
        "don't want to",
        "done",
        "been strong",
        "carrying",
        "worn out",
        "depleted",
    ]
    angry_signals = [
        "angry",
        "furious",
        "sick of",
        "fed up",
        "not fair",
        "pushing back",
        "hate",
        "resentment",
        "doesn't make sense",
        "shouldn't have to",
    ]
    critical_signals = [
        "stupid",
        "failure",
        "should have known",
        "what's wrong with me",
        "disappointed in myself",
        "always do this",
        "never learn",
    ]
    yearning_signals = [
        "want to be seen",
        "want to belong",
        "want to feel",
        "just want",
        "longing",
        "wish someone",
        "want to be known",
        "want connection",
    ]
    avoidant_signals = [
        "keep busy",
        "don't think about",
        "distract",
        "easier not to",
        "avoid",
        "don't go there",
        "push it away",
        "pretend",
    ]

    part_map = [
        ("protective part", protective_signals),
        ("fearful part", fearful_signals),
        ("hopeful part", hopeful_signals),
        ("tired part", tired_signals),
        ("angry part", angry_signals),
        ("critical part", critical_signals),
        ("yearning part", yearning_signals),
        ("avoidant part", avoidant_signals),
    ]

    for part_name, signals in part_map:
        if any(s in msg for s in signals):
            suggestions.append(part_name)

    return suggestions[:3]  # Return max 3 suggested parts


if __name__ == "__main__":
    try:
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        history = require_list_field(data, "history")

        if not message:
            print(json.dumps({"error": "No 'message' field in input."}))
            sys.exit(1)

        result = detect_inner_conflict(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
