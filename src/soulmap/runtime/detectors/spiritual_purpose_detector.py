"""Detect spiritual purpose discernment: aligned action vs driven action or avoidance."""

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

# Single source of truth: skills/frameworks/spiritual-purpose.md,
# "## Activation Signals". Nothing is hardcoded here.
SPIRITUAL_PURPOSE_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/spiritual-purpose.md"), "Activation Signals"
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_spiritual_purpose(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user questioning whether their direction is aligned or driven."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in SPIRITUAL_PURPOSE_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"spiritual_purpose: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "spiritual_purpose_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No spiritual purpose signal. Continue standard pipeline.",
        }

    return {
        "spiritual_purpose_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Spiritual purpose discernment detected. Activate spiritual-purpose.md. "
            "Never tell the user what their purpose is or suggest they should know "
            "their calling by now. Reflect back what you notice about the energy "
            "(aligned or driven) and explore what is underneath the action or "
            "inaction. End with one noticing-oriented question, never a request to "
            "commit or figure it out."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_spiritual_purpose(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
