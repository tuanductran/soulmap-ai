"""Detect sacred feminine/masculine polarity reflection: receptivity vs action balance."""

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

# Single source of truth: skills/frameworks/sacred-feminine-masculine/content/sacred-feminine-masculine.md,
# "## Activation Signals". Nothing is hardcoded here.
SACRED_POLARITY_SIGNALS = load_keyword_section(
    runtime_skill_path("sacred-feminine-masculine"),
    "Activation Signals",
)
_RULES = load_key_value_table(
    runtime_skill_path("sacred-feminine-masculine"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    runtime_skill_path("sacred-feminine-masculine"),
    "Guidance",
)

HistoryMessage = dict[str, str]


def detect_sacred_polarity(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user exploring balance of receptivity and action, surrender and will."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in SACRED_POLARITY_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"sacred_polarity: '{phrase}'")
            break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "sacred_polarity_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "sacred_polarity_detected": True,
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
                detect_sacred_polarity(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
