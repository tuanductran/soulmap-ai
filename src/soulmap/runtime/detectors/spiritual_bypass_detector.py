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
    load_key_value_table,
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

_BYPASS_SCORING = load_key_value_table(_DISCERNMENT_PATH, "Scoring")
_BYPASS_GUIDANCE = load_key_value_table(_DISCERNMENT_PATH, "Guidance")

HistoryMessage = dict[str, str]


def detect_bypass(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect spiritual bypass patterns.

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
            score += int(_BYPASS_SCORING["Dismissing-pain weight"])
            signals.append(f"dismiss: '{phrase}'")
            bypass_type = "dismissing_pain"
            break

    for phrase in PREMATURE_ACCEPTANCE:
        if phrase in msg:
            score += int(_BYPASS_SCORING["Premature-acceptance weight"])
            signals.append(f"premature: '{phrase}'")
            if not bypass_type:
                bypass_type = "premature_acceptance"
            break

    for phrase in SPIRITUAL_INFLATION:
        if phrase in msg:
            score += int(_BYPASS_SCORING["Spiritual-inflation weight"])
            signals.append(f"inflation: '{phrase}'")
            if not bypass_type:
                bypass_type = "spiritual_inflation"
            break

    for phrase in BYPASS_ACCOUNTABILITY:
        if phrase in msg:
            score += int(_BYPASS_SCORING["Accountability-bypass weight"])
            signals.append(f"accountability: '{phrase}'")
            if not bypass_type:
                bypass_type = "bypassing_accountability"
            break

    genuine_count = sum(1 for phrase in GENUINE_INTEGRATION if phrase in msg)
    if genuine_count >= 2:
        score = max(
            0, score - int(_BYPASS_SCORING["Genuine-integration score reduction"])
        )
        signals.append(f"genuine_integration_signals: {genuine_count} (score reduced)")

    if score < int(_BYPASS_SCORING["Minimum detection score"]):
        return {
            "bypass_detected": False,
            "bypass_type": None,
            "score": score,
            "signals": signals,
        }

    guidance_map = _BYPASS_GUIDANCE

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
