"""Detect fear of visibility signals (P8c)."""

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
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/fear-of-visibility.md,
# "## Detection signals". Nothing is hardcoded here.
_VISIBILITY_GROUPS = load_labeled_groups(
    default_skill_path("skills/frameworks/fear-of-visibility.md"), "Detection signals"
)
VISIBILITY_FEAR_SIGNALS = _VISIBILITY_GROUPS["direct visibility fear"]
SHRINKING_SIGNALS = _VISIBILITY_GROUPS["shrinking"]
PUBLIC_EXPRESSION_SIGNALS = _VISIBILITY_GROUPS["public expression"]

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

    # Secondary: shrinking + public/sharing context.
    if (
        any(signal in msg for signal in SHRINKING_SIGNALS)
        and any(signal in msg for signal in PUBLIC_EXPRESSION_SIGNALS)
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
