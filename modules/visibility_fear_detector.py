"""Detect fear of visibility signals (P8c)."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from modules.config import VISIBILITY_FEAR_SIGNALS

HistoryMessage = dict[str, str]
_THRESHOLD = 2


def detect_visibility_fear(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect fear of being seen, heard, or known publicly."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in VISIBILITY_FEAR_SIGNALS:
        if phrase in msg:
            score += 3
            signals.append(f"visibility_fear: '{phrase}'")
            break

    # Secondary: shrinking + public/sharing context
    shrink_refs = (
        "hold back",
        "pull back",
        "stay quiet",
        "go quiet",
        "disappear",
        "invisible",
        "small",
        "hide",
        "hidden",
        "silent",
    )
    public_refs = (
        "share",
        "post",
        "publish",
        "speak up",
        "say something",
        "put out there",
        "show people",
        "let people see",
        "let others see",
    )
    if (
        any(s in msg for s in shrink_refs)
        and any(p in msg for p in public_refs)
        and score == 0
    ):
        score += 2
        signals.append("shrinking + public expression context")

    if score < _THRESHOLD:
        return {
            "visibility_fear_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": "No visibility fear signal. Continue standard pipeline.",
        }

    return {
        "visibility_fear_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": (
            "Fear of visibility detected. Activate fear-of-visibility.md (P8c). "
            "Name the specific contraction at the threshold. Name the protection's intention. "
            "Do NOT push toward action or sharing. End with one visibility question from "
            "deep-inquiry-bank.md (Visibility Questions section)."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        print(
            json.dumps(
                detect_visibility_fear(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
