"""Detect creative drought and disconnection from creative source (P7b)."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.config import CREATIVE_DROUGHT_SIGNALS
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]
_THRESHOLD = 2


def detect_creative_drought(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect creative drought - disconnection from the inner creative source."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in CREATIVE_DROUGHT_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"drought: '{phrase}'")
            break

    # Secondary: creative identity + absence/emptiness language
    creative_id = (
        "as a writer",
        "as an artist",
        "as a creator",
        "my writing",
        "my art",
        "my work",
        "my content",
        "my music",
        "my design",
        "i create",
        "i write",
        "i make",
        "i used to make",
        "i used to write",
        "creative",
    )
    absence = (
        "nothing",
        "empty",
        "blank",
        "dried up",
        "gone quiet",
        "not coming",
        "not flowing",
        "stopped",
        "disappeared",
        "lost it",
        "can't access",
    )
    if (
        any(c in msg for c in creative_id)
        and any(a in msg for a in absence)
        and score == 0
    ):
        score += 2
        signals.append("creative identity + absence language")

    if score < _THRESHOLD:
        return {
            "creative_drought_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No creative drought signal. Continue standard pipeline.",
        }

    return {
        "creative_drought_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Creative drought detected. Activate creative-drought.md (P7b). "
            "Name the specific quality of the silence. Do NOT offer techniques or practices. "
            "Reflect what the drought may be saying. End with one creative drought question from "
            "deep-inquiry-bank.md (Creative Drought Questions section)."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_creative_drought(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
