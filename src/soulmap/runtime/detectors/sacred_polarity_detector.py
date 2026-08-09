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
    default_skill_path,
    load_keyword_section,
)

# Single source of truth: skills/frameworks/sacred-feminine-masculine.md,
# "## Activation Signals". Nothing is hardcoded here.
SACRED_POLARITY_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/sacred-feminine-masculine.md"),
    "Activation Signals",
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_sacred_polarity(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user exploring balance of receptivity and action, surrender and will."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in SACRED_POLARITY_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"sacred_polarity: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "sacred_polarity_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No sacred polarity signal. Continue standard pipeline.",
        }

    return {
        "sacred_polarity_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Sacred feminine/masculine polarity reflection detected. Activate "
            "sacred-feminine-masculine.md. Never assign feminine or masculine to the "
            "user based on gender, and never prescribe how the balance should look. "
            "Reflect back the pattern they are living and explore what it reveals "
            "about their relationship to both energies. End with one awareness-"
            "oriented question, never a prescription for balance."
        ),
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
