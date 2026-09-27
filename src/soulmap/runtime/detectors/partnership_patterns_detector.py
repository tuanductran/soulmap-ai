"""Detect recurring patterns specific to dating and partner-seeking."""

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

# Single source of truth: skills/soulmate/partnership-patterns.md,
# "## Activation Signals". Nothing is hardcoded here.
PARTNERSHIP_PATTERNS_SIGNALS = load_keyword_section(
    default_skill_path("skills/soulmate/partnership-patterns.md"), "Activation Signals"
)
_RULES = load_key_value_table(
    default_skill_path("skills/soulmate/partnership-patterns.md"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    default_skill_path("skills/soulmate/partnership-patterns.md"), "Guidance"
)


HistoryMessage = dict[str, str]


def detect_partnership_patterns(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect a recurring pattern specific to dating or partner-seeking."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in PARTNERSHIP_PATTERNS_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"partnership_pattern: '{phrase}'")
            break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "partnership_pattern_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "partnership_pattern_detected": True,
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
                detect_partnership_patterns(message, history),
                ensure_ascii=False,
                indent=2,
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
