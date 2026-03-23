"""Detect empath boundary dissolution and energetic overwhelm (P8d)."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from modules.config import EMPATH_SIGNALS

HistoryMessage = dict[str, str]
_THRESHOLD = 2


def detect_empath_overwhelm(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect empath boundary dissolution and absorption of others' emotions."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in EMPATH_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"empath: '{phrase}'")
            break

    # Secondary: drain/exhaustion + people/others context
    drain = (
        "drained",
        "exhausted",
        "depleted",
        "worn out",
        "tired after",
        "need to recover",
    )
    people_ctx = (
        "being around people",
        "after being with",
        "after spending time",
        "after the visit",
        "family gatherings",
        "around my family",
        "at work",
        "in crowds",
        "in groups",
    )
    if (
        any(d in msg for d in drain)
        and any(p in msg for p in people_ctx)
        and score == 0
    ):
        score += 2
        signals.append("drain + people context")

    if score < _THRESHOLD:
        return {
            "empath_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No empath signal. Continue standard pipeline.",
        }

    return {
        "empath_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Empath boundary dissolution detected. Activate empath-boundary.md (P8d). "
            "Name the dispersion first. Acknowledge what the sensitivity makes possible. "
            "Locate the specific weight. End with one empath question from "
            "deep-inquiry-bank.md (Empath Questions section). "
            "Do NOT suggest specific energy protection techniques."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_empath_overwhelm(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
