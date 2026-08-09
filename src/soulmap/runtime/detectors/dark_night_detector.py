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
    default_skill_path,
    load_keyword_section,
)

# Single source of truth: skills/frameworks/dark-night-of-soul.md,
# "## Activation Signals". Nothing is hardcoded here.
DARK_NIGHT_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/dark-night-of-soul.md"), "Activation Signals"
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_dark_night(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect spiritual dryness, loss of faith, or disconnection from the sacred."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in DARK_NIGHT_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"dark_night: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "dark_night_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No dark night signal. Continue standard pipeline.",
        }

    return {
        "dark_night_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Dark Night of the Soul territory detected. Activate dark-night-of-soul.md. "
            "Do not offer premature reassurance, spiritual prescriptions, or reframe the "
            "emptiness as growth. Name the territory honestly and stay present to the "
            "not-knowing alongside the user. End with one presence-oriented question, "
            "never a request for action or practice."
        ),
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
