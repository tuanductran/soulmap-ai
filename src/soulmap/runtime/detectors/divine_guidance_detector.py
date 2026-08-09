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
    default_skill_path,
    load_keyword_section,
)

# Single source of truth: skills/frameworks/divine-guidance.md,
# "## Activation Signals". Nothing is hardcoded here.
DIVINE_GUIDANCE_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/divine-guidance.md"), "Activation Signals"
)

HistoryMessage = dict[str, str]
_THRESHOLD = 3


def detect_divine_guidance(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user trying to discern inner knowing from fear or projection."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in DIVINE_GUIDANCE_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"divine_guidance: '{phrase}'")
            break

    if score < _THRESHOLD:
        return {
            "divine_guidance_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No divine guidance signal. Continue standard pipeline.",
        }

    return {
        "divine_guidance_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Divine guidance discernment detected. Activate divine-guidance.md. "
            "Never confirm whether guidance is 'real' or from spirits/guides, and never "
            "tell the user what to do based on their guidance. Reflect back the "
            "qualities of what they sensed and explore how they can test it against "
            "their own deepest knowing. End with one discernment-oriented question."
        ),
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
