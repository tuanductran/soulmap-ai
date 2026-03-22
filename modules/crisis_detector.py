"""Classify immediate safety risk from a single user message."""

import json
import re
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_non_empty_str_field,
)
from modules.config import CRISIS_TIER1, CRISIS_TIER2, GRANDIOSITY_SIGNALS
from modules.text_normalization import normalize_message_text

CRISIS_TIER1_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "do not want to keep living",
        re.compile(
            r"\bi\s+(?:do not|don't|dont)\s+want\s+to\s+keep\s+"
            r"(?:living|going)\b"
        ),
    ),
    (
        "do not want to be alive",
        re.compile(r"\bi\s+(?:do not|don't|dont)\s+want\s+to\s+be\s+alive\b"),
    ),
    (
        "thinking about suicide",
        re.compile(
            r"\bi(?:'m| am)?\s+(?:thinking|thought)\s+about\s+"
            r"(?:suicide|killing myself|ending my life|hurting myself)\b"
        ),
    ),
]

FAREWELL_CRISIS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "i am saying goodbye",
        re.compile(r"\bi(?:'m| am)\s+saying\s+goodbye\b"),
    ),
    (
        "this is my last message",
        re.compile(r"\b(?:this is|here is|sending)\s+my\s+(?:last|final)\s+message\b"),
    ),
    (
        "i will not be here",
        re.compile(
            r"\bi\s+(?:won't|will not)\s+be\s+here(?:\s+(?:anymore|tomorrow))?\b"
        ),
    ),
]

NON_CRISIS_FAREWELL_CONTEXT: list[re.Pattern[str]] = [
    re.compile(r"\bevery day feels like goodbye\b"),
    re.compile(r"\bevery day is (?:another )?goodbye\b"),
    re.compile(r"\bsaying goodbye slowly\b"),
    re.compile(r"\bmonths of goodbye\b"),
]


def detect_crisis(message: str) -> dict:
    """
    Scan a single user message for crisis signals.

    Returns:
        Dict with: level (str), action (str), signals (list), response_guidance (str)
    """
    msg = normalize_message_text(message)
    signals_found = []

    for signal in CRISIS_TIER1:
        if signal in msg:
            signals_found.append(signal)

    for label, pattern in CRISIS_TIER1_PATTERNS:
        if pattern.search(msg) and label not in signals_found:
            signals_found.append(label)

    in_non_crisis_farewell_context = any(
        pattern.search(msg) for pattern in NON_CRISIS_FAREWELL_CONTEXT
    )
    if not in_non_crisis_farewell_context:
        for label, pattern in FAREWELL_CRISIS_PATTERNS:
            if pattern.search(msg) and label not in signals_found:
                signals_found.append(label)

    if signals_found:
        return {
            "level": "CRISIS_TIER1",
            "tier": 1,
            "action": "IMMEDIATE_SAFETY_RESPONSE",
            "signals": signals_found,
            "response_guidance": (
                "STOP. Do not use the five-step framework. Do not offer reflective questions. "
                "1. Acknowledge with full presence in 1-2 sentences. "
                "2. Express care clearly. "
                "3. Provide crisis line for the user's region immediately. "
                "Known crisis lines: "
                "Vietnam: 1800 599 920 (free, 24/7) | "
                "US: 988 (call or text) | "
                "UK: Samaritans 116 123 | "
                "AU: Lifeline 13 11 14 | "
                "International: findahelpline.com | "
                "If region is unknown, use findahelpline.com and include the most likely local line. "
                "4. Encourage them to reach out to a real person right now. "
                "No emoji. No spiritual framing. Words only. "
                "Example: 'I hear you. What you are carrying right now is real and it is heavy. "
                "Please reach out to a crisis support line right now - you do not have to be alone with this. "
                "[include region-appropriate line above]'"
            ),
        }

    tier2_found = []
    for signal in CRISIS_TIER2:
        if signal in msg:
            tier2_found.append(signal)

    if tier2_found:
        return {
            "level": "CRISIS_TIER2",
            "tier": 2,
            "action": "PRESENCE_FIRST_MANDATORY",
            "signals": tier2_found,
            "response_guidance": (
                "High distress detected. Presence-first response mandatory. "
                "Skip the five-step framework entirely for now. "
                "1. Acknowledge what they said - reflect it back without adding any interpretation. "
                "2. Stay close. One short, warm sentence at a time. "
                "3. If distress escalates or any Tier 1 signal appears - escalate immediately. "
                "No emoji. No frameworks. No questions yet."
            ),
        }

    grandiosity_found = []
    for signal in GRANDIOSITY_SIGNALS:
        if signal in msg:
            grandiosity_found.append(signal)

    if grandiosity_found:
        return {
            "level": "GRANDIOSITY_SIGNAL",
            "tier": 0,
            "action": "DO_NOT_AFFIRM_REDIRECT_GENTLY",
            "signals": grandiosity_found,
            "response_guidance": (
                "Spiritual grandiosity signal detected. Do NOT affirm the grandiosity. "
                "Do NOT dismiss the experience entirely. "
                "Redirect gently toward grounded inquiry. "
                "Example: 'I hear how significant this feels for you. "
                "I wonder - what does this sense of mission feel like when it is most grounded in your everyday life?'"
            ),
        }

    return {
        "level": "NO_CRISIS",
        "tier": 0,
        "action": "CONTINUE_NORMAL",
        "signals": [],
        "response_guidance": "No crisis signals detected. Proceed with normal SoulMap response framework.",
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message = require_non_empty_str_field(data, "message")
        result = detect_crisis(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
