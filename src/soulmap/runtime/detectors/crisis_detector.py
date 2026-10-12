"""Classify immediate safety risk from a single user message."""

import json
import re
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_non_empty_str_field,
)
from soulmap.runtime.io.text_normalization import normalize_message_text
from soulmap.runtime.knowledge.crisis_language_packs import (
    CRISIS_TIER1,
    CRISIS_TIER2,
    GRANDIOSITY_SIGNALS,
)

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
            r"(?:suicide|killing myself|ending my life|ending it all|hurting myself)\b"
        ),
    ),
    (
        "vietnamese no longer want to live",
        re.compile(
            r"\b(?:tôi|em|mình)\s+(?:không|chẳng|ko)\s+(?:muốn|muon)\s+"
            r"(?:sống|song)(?:\s+nữa)?\s*(?:[.!?…]|$)"
        ),
    ),
    (
        "spanish no longer want to live",
        re.compile(
            r"\b(?:ya\s+)?no\s+quiero\s+(?:seguir\s+)?viv(?:ir|iendo)"
            r"(?:\s+m[aá]s)?\s*(?:[.!?…]|$)"
        ),
    ),
    (
        "french no longer want to live",
        re.compile(
            r"\b(?:je\s+ne\s+veux\s+plus|je\s+veux\s+pas)\s+vivre"
            r"\s*(?:[.!?…]|$)"
        ),
    ),
    (
        "chinese no longer want to live",
        re.compile(
            r"(?:我\s*)?(?:不想|不愿)\s*(?:再\s*)?(?:活(?:着)?|继续活)\s*(?:[。\uFF01\uFF1F]|$)"
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

# These Spanish strings contain a Tier 1 phrase as a location preference, not a
# statement about continuing to live. Keep this exception limited to the literal
# signals it disambiguates so other crisis signals in the same message still surface.
_SPANISH_LOCATION_NEAR_MISS = re.compile(r"\bno quiero vivir m[aá]s lejos\b")


def _is_literal_tier1_near_miss(signal: str, message: str) -> bool:
    return signal in {"no quiero vivir mas", "no quiero vivir más"} and bool(
        _SPANISH_LOCATION_NEAR_MISS.search(message)
    )


def detect_crisis(message: str) -> dict:
    """Scan a single user message for crisis signals.

    Returns:
        Dict with: level (str), action (str), signals (list), response_guidance (str)
    """
    msg = normalize_message_text(message)
    signals_found = []

    for signal in CRISIS_TIER1:
        if signal in msg and not _is_literal_tier1_near_miss(signal, msg):
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
                "1. Briefly acknowledge the immediate risk and express care in 1-2 sentences; do not minimize or promise outcomes. "
                "2. Give urgent safety guidance: if danger may be immediate, contact local emergency services and move near a trusted person if safe. "
                "3. Share region-appropriate crisis resources alongside or immediately after that first response; never delay initial safety guidance to search. "
                "Resource starting points only; verify the user's region, contact details, and current availability before making claims: "
                "Vietnam: HOPE 0865 044 400 (hours and availability must be verified; do not claim 24/7) | "
                "US: 988 (call or text; verify current regional availability) | "
                "UK: Samaritans 116 123 (verify current availability) | "
                "AU: Lifeline 13 11 14 (verify current availability) | "
                "International: findahelpline.com | "
                "If region is unknown, offer findahelpline.com as a starting point; do not guess the user's country or invent a local line. "
                "4. Encourage them to reach out to a trusted real person right now. "
                "No emoji. No spiritual framing. Words only. "
                "Example: 'I hear you. What you are carrying right now is real and it is heavy. "
                "If you may be in immediate danger, contact local emergency services and get near someone you trust if safe. "
                "[include a region-appropriate resource only when its details are verified]'"
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
