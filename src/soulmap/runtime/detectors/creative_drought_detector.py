"""Detect creative drought and disconnection from creative source (P7b)."""

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

# Single source of truth: skills/frameworks/creative-drought.md,
# "## Activation Signals". Nothing is hardcoded here.
CREATIVE_DROUGHT_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/creative-drought.md"), "Activation Signals"
)
_RULES = load_key_value_table(
    default_skill_path("skills/frameworks/creative-drought.md"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    default_skill_path("skills/frameworks/creative-drought.md"), "Guidance"
)


HistoryMessage = dict[str, str]


def detect_creative_drought(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect creative drought - disconnection from the inner creative source."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in CREATIVE_DROUGHT_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"drought: '{phrase}'")
            break

    # Secondary: creative identity + absence/emptiness language
    creative_id = load_keyword_section(
        default_skill_path("skills/frameworks/creative-drought.md"), "Creative-identity signals"
    )
    absence = load_keyword_section(
        default_skill_path("skills/frameworks/creative-drought.md"), "Absence signals"
    )
    if (
        any(c in msg for c in creative_id)
        and any(a in msg for a in absence)
        and score == 0
    ):
        score += int(_RULES["Creative-identity plus absence weight"])
        signals.append("creative identity + absence language")

    if score < int(_RULES["Minimum detection score"]):
        return {
            "creative_drought_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "creative_drought_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": _GUIDANCE["detected"],
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_creative_drought(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
