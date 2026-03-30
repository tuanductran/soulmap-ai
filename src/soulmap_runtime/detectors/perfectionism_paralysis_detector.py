"""Detect perfectionism as paralysis - the not-starting/not-finishing/not-releasing pattern (P7c)."""

from __future__ import annotations

import json
import sys

from soulmap_runtime.config import (
    PERFECTIONISM_PARALYSIS_SIGNALS,
    PERFECTIONISM_SIGNALS,
)
from soulmap_runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]
_THRESHOLD = 2


def detect_perfectionism_paralysis(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect perfectionism operating as a stop - paralysis at the threshold of starting or releasing."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    # Paralysis-specific signals score higher (these are the stopping patterns)
    for phrase in PERFECTIONISM_PARALYSIS_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"paralysis: '{phrase}'")
            break

    # General perfectionism signals add secondary score
    for phrase in PERFECTIONISM_SIGNALS:
        if phrase in msg and score == 0:
            score += 2
            signals.append(f"perfectionism: '{phrase}'")
            break

    # Check for pattern persistence in history (paralysis appears repeatedly)
    if history and score > 0:
        hist_text = " ".join(
            m.get("content", "").lower()
            for m in history[-4:]
            if isinstance(m, dict) and m.get("role") == "user"
        )
        repeat_signals = (
            "still not ready",
            "still not finished",
            "still can't",
            "again",
            "still working on",
        )
        if any(r in hist_text for r in repeat_signals):
            score += 1
            signals.append("pattern_persistence_in_history")

    if score < _THRESHOLD:
        return {
            "perfectionism_paralysis_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No perfectionism paralysis signal. Continue standard pipeline.",
        }

    return {
        "perfectionism_paralysis_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Perfectionism paralysis detected. Activate perfectionism-paralysis.md (P7c). "
            "Name the specific shape of the stop. Name what the perfectionism is protecting. "
            "Do NOT advise 'just ship it' or offer techniques. "
            "End with one perfectionism question from deep-inquiry-bank.md "
            "(Perfectionism Questions section)."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_perfectionism_paralysis(message, history),
                ensure_ascii=False,
                indent=2,
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
