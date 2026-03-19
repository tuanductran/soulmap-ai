"""Detect spiritual language that may skip felt emotional reality."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

BYPASS_DISMISS = [
    "everything happens for a reason",
    "it was meant to be",
    "the universe has a plan",
    "this is my karma",
    "i'm meant to learn from this",
    "it's all happening for my highest good",
    "i just need to let go",
    "i need to surrender",
    "i need to accept it",
    "i shouldn't be attached",
    "i need to raise my vibration",
    "this is just an ego reaction",
    "i need to transcend this",
    "at a soul level i chose this",
    "my higher self knows why",
    "i'm being tested",
    "this is a lesson i needed",
    "everything is perfect as it is",
    "i just need to be grateful",
]

PREMATURE_ACCEPTANCE = [
    "i've already forgiven them",
    "i'm at peace with it",
    "i've moved on",
    "i'm over it now",
    "i've accepted it",
    "i'm grateful for the lesson",
    "it made me stronger",
    "everything worked out for the best",
    "i'm not angry anymore",
    "i've released it",
]

SPIRITUAL_INFLATION = [
    "as a lightworker",
    "as an empath i feel",
    "i'm highly sensitive so",
    "my vibration is too high for",
    "i've ascended past",
    "from a 5d perspective",
    "i've done the work",
    "i'm very spiritually advanced",
    "most people can't understand",
    "i operate at a different level",
]

BYPASS_ACCOUNTABILITY = [
    "it was their karma not mine",
    "they were my teacher",
    "i called this into my life",
    "i manifested this situation",
    "i attracted them for a reason",
    "we were meant to cross paths",
    "they reflected my shadow to me",
    "the universe sent them",
]

GENUINE_INTEGRATION = [
    "still feeling",
    "still processing",
    "even though i know",
    "trying to accept but",
    "working on accepting",
    "i feel angry and also",
    "both are true",
    "complicated",
    "haven't fully",
    "still sitting with",
    "it's hard even though",
]


def detect_bypass(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect spiritual bypass patterns.

    Key distinction:
    - Genuine spirituality supports emotional processing
    - Spiritual bypass uses spirituality to skip it

    Returns secondary_layer flag — never primary framework.
    """
    msg = message.lower().strip()
    signals = []
    score = 0
    bypass_type = None

    for phrase in BYPASS_DISMISS:
        if phrase in msg:
            score += 2
            signals.append(f"dismiss: '{phrase}'")
            bypass_type = "dismissing_pain"
            break

    for phrase in PREMATURE_ACCEPTANCE:
        if phrase in msg:
            score += 2
            signals.append(f"premature: '{phrase}'")
            if not bypass_type:
                bypass_type = "premature_acceptance"
            break

    for phrase in SPIRITUAL_INFLATION:
        if phrase in msg:
            score += 2
            signals.append(f"inflation: '{phrase}'")
            if not bypass_type:
                bypass_type = "spiritual_inflation"
            break

    for phrase in BYPASS_ACCOUNTABILITY:
        if phrase in msg:
            score += 2
            signals.append(f"accountability: '{phrase}'")
            if not bypass_type:
                bypass_type = "bypassing_accountability"
            break

    genuine_count = sum(1 for phrase in GENUINE_INTEGRATION if phrase in msg)
    if genuine_count >= 2:
        score = max(0, score - 2)
        signals.append(f"genuine_integration_signals: {genuine_count} (score reduced)")

    if score < 2:
        return {
            "bypass_detected": False,
            "bypass_type": None,
            "score": score,
            "signals": signals,
        }

    guidance_map = {
        "dismissing_pain": (
            "Bypass type: using spiritual framework to dismiss pain before it's been felt. "
            "Use 'ground the mystical' pattern from skills/voice/persona-voice.md: "
            "'If this is [acceptance/surrender/lesson] — it still needs a body to live in. "
            "What is actually happening for you emotionally right now, underneath the framework?'"
        ),
        "premature_acceptance": (
            "Bypass type: premature acceptance — claiming peace before processing. "
            "Gently check what's underneath: 'That sounds like peace. "
            "Is there anything underneath it that hasn't been fully felt yet — "
            "something that arrived before the peace did?'"
        ),
        "spiritual_inflation": (
            "Bypass type: spiritual identity being used to create distance from vulnerability. "
            "Do not challenge the identity — ground it: "
            "'What does [being an empath / your sensitivity / your awareness] feel like "
            "in this specific situation, in your body, right now?'"
        ),
        "bypassing_accountability": (
            "Bypass type: spiritual framing being used to avoid looking at own role or to "
            "over-spiritualize a human situation. Gently bring back to the personal: "
            "'Setting the cosmic frame aside for a moment — what did this feel like for you, "
            "as a person, not as a soul on a journey?'"
        ),
    }

    return {
        "bypass_detected": True,
        "bypass_type": bypass_type,
        "score": score,
        "signals": signals,
        "note": "SECONDARY LAYER — gently ground the spiritual language before exploring.",
        "recommendation": guidance_map.get(bypass_type or "", ""),
    }


if __name__ == "__main__":
    try:
        data = parse_json_object(sys.stdin.read().strip())
        result = detect_bypass(
            require_str_field(data, "message"),
            require_list_field(data, "history"),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
