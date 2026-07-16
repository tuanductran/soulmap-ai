"""Detect spiritual language that may skip felt emotional reality."""

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
    load_keyword_section,
)

# Single source of truth: skills/spiritual/spiritual-discernment.md,
# "## Detection signal reference". Nothing is hardcoded here — the phrase
# lists are parsed straight from that Markdown skill.
_DISCERNMENT_PATH = default_skill_path("skills/spiritual/spiritual-discernment.md")
BYPASS_DISMISS = load_keyword_section(_DISCERNMENT_PATH, "Bypass: Dismissing Pain")
PREMATURE_ACCEPTANCE = load_keyword_section(
    _DISCERNMENT_PATH, "Bypass: Premature Acceptance"
)
SPIRITUAL_INFLATION = load_keyword_section(
    _DISCERNMENT_PATH, "Bypass: Spiritual Inflation"
)
BYPASS_ACCOUNTABILITY = load_keyword_section(
    _DISCERNMENT_PATH, "Bypass: Bypassing Accountability"
)
GENUINE_INTEGRATION = load_keyword_section(
    _DISCERNMENT_PATH, "Genuine Integration Signals"
)

HistoryMessage = dict[str, str]


def detect_bypass(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect spiritual bypass patterns.

    Key distinction:
    - Genuine spirituality supports emotional processing
    - Spiritual bypass uses spirituality to skip it

    Returns secondary_layer flag  -  never primary framework.
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
            "'If this is [acceptance/surrender/lesson]  -  it still needs a body to live in. "
            "What is actually happening for you emotionally right now, underneath the framework?'"
        ),
        "premature_acceptance": (
            "Bypass type: premature acceptance  -  claiming peace before processing. "
            "Gently check what's underneath: 'That sounds like peace. "
            "Is there anything underneath it that hasn't been fully felt yet  -  "
            "something that arrived before the peace did?'"
        ),
        "spiritual_inflation": (
            "Bypass type: spiritual identity being used to create distance from vulnerability. "
            "Do not challenge the identity  -  ground it: "
            "'What does [being an empath / your sensitivity / your awareness] feel like "
            "in this specific situation, in your body, right now?'"
        ),
        "bypassing_accountability": (
            "Bypass type: spiritual framing being used to avoid looking at own role or to "
            "over-spiritualize a human situation. Gently bring back to the personal: "
            "'Setting the cosmic frame aside for a moment  -  what did this feel like for you, "
            "as a person, not as a soul on a journey?'"
        ),
    }

    return {
        "bypass_detected": True,
        "bypass_type": bypass_type,
        "score": score,
        "signals": signals,
        "note": "SECONDARY LAYER  -  gently ground the spiritual language before exploring.",
        "recommendation": guidance_map.get(bypass_type or "", ""),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        result = detect_bypass(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
