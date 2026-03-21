"""Classify immediate safety risk from a single user message."""

import json
import sys

from modules.cli_payload import parse_json_object, require_str_field

CRISIS_TIER1 = [
    "want to die",
    "want to end my life",
    "end it all",
    "kill myself",
    "not want to be here anymore",
    "don't want to be here anymore",
    "dont want to be here anymore",
    "not want to be here",
    "better off without me",
    "don't want to exist",
    "better off dead",
    "thinking about suicide",
    "thinking about hurting myself",
    "thinking about ending my life",
    "planning to kill myself",
    "planning to end my life",
    "planning to hurt myself",
    "i won't be here",
    "saying goodbye",
    "final message",
    "last message",
    "can't go on",
    "no reason to live",
    "life isn't worth",
    "hurt myself",
    "hurting myself",
    "cutting myself",
    "harming myself",
    "self-harm",
    "want to hurt myself",
    "want to harm myself",
    "burn myself",
    "i am god",
    "i have a divine mission no one understands",
    "they are following me",
    "voices are telling me to",
    "i am being controlled",
    "i am not real",
]

CRISIS_TIER2 = [
    "i can't take it anymore",
    "i'm falling apart",
    "completely broken",
    "i have nothing left",
    "everything is pointless",
    "nothing matters",
    "i feel nothing",
    "i'm numb to everything",
    "i don't feel real",
    "i'm disappearing",
    "i feel empty inside",
    "there's no hope",
    "i'm trapped",
    "i see no way out",
    "i'm exhausted from living",
    "abuse",
    "he hurt me",
    "she hurt me",
    "they hurt me",
    "being abused",
    "violence at home",
    "i'm not safe",
]

GRANDIOSITY_SIGNALS = [
    "i am the chosen one",
    "only i can save",
    "i have a cosmic mission",
    "i am more evolved than",
    "i have ascended",
    "i am enlightened and no one understands",
    "i am a twin flame runner",
    "i have been sent here",
]


def detect_crisis(message: str) -> dict:
    """
    Scan a single user message for crisis signals.

    Returns:
        Dict with: level (str), action (str), signals (list), response_guidance (str)
    """
    msg = message.lower().strip()
    signals_found = []

    for signal in CRISIS_TIER1:
        if signal in msg:
            signals_found.append(signal)

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
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        if not message:
            print(json.dumps({"error": "No 'message' field in input."}))
            sys.exit(1)

        result = detect_crisis(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
