"""Detect soulmate longing: the ache of not having found a partner."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from soulmap.runtime.knowledge.keyword_lists import (
    load_key_value_table,
    load_keyword_section,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/soulmate/soulmate-longing.md,
# "## Activation Signals". Nothing is hardcoded here.
SOULMATE_LONGING_SIGNALS = load_keyword_section(
    runtime_skill_path("soulmate-longing"), "Activation Signals"
)
_RULES = load_key_value_table(
    runtime_skill_path("soulmate-longing"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    runtime_skill_path("soulmate-longing"), "Guidance"
)


HistoryMessage = dict[str, str]


def detect_soulmate_longing(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the ache of not having found a partner, or grief about a connection."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in SOULMATE_LONGING_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"soulmate_longing: '{phrase}'")
            break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "soulmate_longing_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "soulmate_longing_detected": True,
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
                detect_soulmate_longing(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
