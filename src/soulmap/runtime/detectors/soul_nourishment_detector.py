"""Detect soul nourishment recognition: what genuinely feeds the user's spirit."""

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

# Single source of truth: skills/frameworks/soul-nourishment.md,
# "## Activation Signals". Nothing is hardcoded here.
SOUL_NOURISHMENT_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/soul-nourishment.md"), "Activation Signals"
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_soul_nourishment(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user naming or questioning what genuinely nourishes them."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in SOUL_NOURISHMENT_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"soul_nourishment: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "soul_nourishment_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No soul nourishment signal. Continue standard pipeline.",
        }

    return {
        "soul_nourishment_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Soul nourishment recognition detected. Activate soul-nourishment.md. "
            "Do not prescribe practices, routines, or generic self-care advice. "
            "Reflect back the aliveness or rightness the user recognized and explore "
            "what it reveals about what their soul actually needs. End with one "
            "noticing-oriented question, not a request for commitment or practice."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_soul_nourishment(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
