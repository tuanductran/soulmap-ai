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
    load_keyword_section,
)

# Single source of truth: skills/soulmate/partnership-patterns.md,
# "## Activation Signals". Nothing is hardcoded here.
PARTNERSHIP_PATTERNS_SIGNALS = load_keyword_section(
    default_skill_path("skills/soulmate/partnership-patterns.md"), "Activation Signals"
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_partnership_patterns(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect a recurring pattern specific to dating or partner-seeking."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in PARTNERSHIP_PATTERNS_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"partnership_pattern: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "partnership_pattern_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": (
                "No partnership pattern signal. Continue standard pipeline."
            ),
        }

    return {
        "partnership_pattern_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Partnership pattern detected. Activate partnership-patterns.md. Keep "
            "the lens inward: the pattern is information about the user, not a "
            "verdict on the people they dated. Never tell the user who to date or "
            "promise that changing the pattern will produce a partner. End with "
            "one question about what the pattern involves in the user, not the "
            "other people."
        ),
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
