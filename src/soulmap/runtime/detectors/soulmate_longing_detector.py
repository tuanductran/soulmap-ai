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
    default_skill_path,
    load_keyword_section,
)

# Single source of truth: skills/soulmate/soulmate-longing.md,
# "## Activation Signals". Nothing is hardcoded here.
SOULMATE_LONGING_SIGNALS = load_keyword_section(
    default_skill_path("skills/soulmate/soulmate-longing.md"), "Activation Signals"
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_soulmate_longing(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the ache of not having found a partner, or grief about a connection."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in SOULMATE_LONGING_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"soulmate_longing: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "soulmate_longing_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No soulmate longing signal. Continue standard pipeline.",
        }

    return {
        "soulmate_longing_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Soulmate longing detected. Activate soulmate-longing.md. Never confirm "
            "that a specific person is the user's soulmate, and never predict "
            "whether or when the user will meet one. Reflect the ache on its own "
            "terms. End with one question that returns to what the longing is "
            "asking for, not a request for the user to name or rank candidates."
        ),
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
