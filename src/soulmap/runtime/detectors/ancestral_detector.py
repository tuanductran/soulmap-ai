"""Detect intergenerational and ancestral pattern recognition signals (P8b)."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.config import ANCESTRAL_SIGNALS
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]
_THRESHOLD = 2


def detect_ancestral(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect intergenerational/ancestral pattern recognition."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in ANCESTRAL_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"ancestral: '{phrase}'")
            break

    # Secondary signals: parent references + pattern language together
    parent_refs = (
        "my mother",
        "my father",
        "my parents",
        "my grandmother",
        "my grandfather",
        "my family",
        "growing up",
        "as a child",
        "when i was young",
    )
    pattern_refs = (
        "same pattern",
        "same thing",
        "same way",
        "always did",
        "always said",
        "was taught",
        "was raised",
        "never showed",
        "never said",
        "couldn't show",
        "passed this",
        "passed it",
        "this too",
        "like them",
    )

    has_parent = any(p in msg for p in parent_refs)
    has_pattern = any(p in msg for p in pattern_refs)
    if has_parent and has_pattern and score == 0:
        score += 2
        signals.append("parent_ref + pattern_language")

    if score < _THRESHOLD:
        return {
            "ancestral_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No ancestral signal. Continue standard pipeline.",
        }

    return {
        "ancestral_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Ancestral pattern recognition detected. Activate ancestral-patterns.md (P8b). "
            "Hold both truths: the wound is real AND the one who passed it was also wounded. "
            "Do NOT push toward forgiveness. End with one ancestral question from "
            "deep-inquiry-bank.md (Ancestral Questions section)."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(detect_ancestral(message, history), ensure_ascii=False, indent=2)
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
