"""Detect Dark Night of the Soul territory: spiritual dryness, doubt, disconnection."""

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

# Single source of truth: skills/frameworks/dark-night-of-soul.md,
# "## Activation Signals". Nothing is hardcoded here.
DARK_NIGHT_SIGNALS = load_keyword_section(
    runtime_skill_path("dark-night-of-soul"), "Activation Signals"
)
_RULES = load_key_value_table(
    runtime_skill_path("dark-night-of-soul"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    runtime_skill_path("dark-night-of-soul"), "Guidance"
)


HistoryMessage = dict[str, str]


def detect_dark_night(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect spiritual dryness, loss of faith, or disconnection from the sacred."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in DARK_NIGHT_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"dark_night: '{phrase}'")
            break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "dark_night_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "dark_night_detected": True,
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
                detect_dark_night(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
