"""Detect divine guidance discernment: inner knowing vs fear, projection, or wishful thinking."""

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

# Single source of truth: skills/frameworks/divine-guidance.md,
# "## Activation Signals". Nothing is hardcoded here.
DIVINE_GUIDANCE_SIGNALS = load_keyword_section(
    runtime_skill_path("divine-guidance"), "Activation Signals"
)
_RULES = load_key_value_table(
    runtime_skill_path("divine-guidance"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(runtime_skill_path("divine-guidance"), "Guidance")


HistoryMessage = dict[str, str]


def detect_divine_guidance(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user trying to discern inner knowing from fear or projection."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in DIVINE_GUIDANCE_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"divine_guidance: '{phrase}'")
            break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "divine_guidance_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "divine_guidance_detected": True,
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
                detect_divine_guidance(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
