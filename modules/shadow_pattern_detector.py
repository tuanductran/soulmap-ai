"""Detect repeated external frustrations that may point to shadow work."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from modules.config import (
    AVOIDANCE_SIGNALS,
    EXTERNAL_REPEAT_SIGNALS,
    OVERTHINKING_SIGNALS,
    PEOPLE_PLEASING_SIGNALS,
    PERFECTIONISM_SIGNALS,
    WITHDRAWAL_SIGNALS,
)

HistoryMessage = dict[str, str]


def detect_shadow_patterns(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect shadow pattern signals in the current message and recent history.

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
            score += 2
            external_frustration = True
            break

    pattern_checks = [
        ("avoidance", AVOIDANCE_SIGNALS, 3),
        ("people_pleasing", PEOPLE_PLEASING_SIGNALS, 3),
        ("overthinking", OVERTHINKING_SIGNALS, 2),
        ("withdrawal", WITHDRAWAL_SIGNALS, 3),
        ("perfectionism", PERFECTIONISM_SIGNALS, 2),
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
        ][-5:]

        external_count = sum(
            1
            for past in recent_user
            if any(phrase in past for phrase in EXTERNAL_REPEAT_SIGNALS[:10])
        )
        if external_count >= 2:
            score += 3
            external_frustration = True

    if score < 2:
        return {
            "shadow_detected": False,
            "patterns_found": [],
            "is_external_frustration": external_frustration,
            "score": score,
            "recommendation": "No shadow pattern signals detected. Continue standard pipeline.",
        }

    if patterns_found:
        pattern_list = ", ".join(patterns_found)
        recommendation = (
            f"Shadow pattern(s) detected: {pattern_list}. "
            "Activate Shadow Pattern Revealer from skills/frameworks/shadow-patterns.md. "
            "Frame as possibility ONLY  -  never as fact. "
            f"Use possibility language: 'Sometimes patterns like this appear when...' "
            "Reflect the protective intention behind the pattern. "
            "Do NOT accuse. Return ownership immediately after reflection. "
            "End with one shadow-specific question from skills/meta/deep-inquiry-bank.md  -  "
            "'Shadow-Specific Questions' section. "
            "One reflection only  -  if user rejects, honor it and move on."
        )
    elif external_frustration:
        recommendation = (
            "Repeated external frustration detected  -  no specific shadow pattern identified yet. "
            "Explore gently using the projection principle from skills/frameworks/shadow-patterns.md. "
            "Ask: what is it about this particular thing that keeps getting to you? "
            "Do not name a shadow pattern until you have more information."
        )
    else:
        recommendation = (
            "Mild shadow signals. Proceed with standard MIRROR response but stay alert "
            "for shadow patterns emerging across the conversation."
        )

    SELF_CRITIC_SIGNALS = [
        "i'm so stupid",
        "i'm pathetic",
        "i hate myself",
        "what's wrong with me",
        "i can't do anything right",
        "i'm my own worst enemy",
        "i deserve this",
        "i'm so disappointed in myself",
        "i'm worthless",
    ]
    for phrase in SELF_CRITIC_SIGNALS:
        if phrase in msg:
            patterns_found.append("self_criticism")
            score += 3
            break

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
