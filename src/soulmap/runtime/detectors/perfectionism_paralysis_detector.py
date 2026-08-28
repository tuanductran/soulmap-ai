"""Detect perfectionism as paralysis - the not-starting/not-finishing/not-releasing pattern (P7c)."""

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

# Single source of truth: skills/frameworks/perfectionism-paralysis.md and
# skills/frameworks/shadow-patterns.md. Nothing is hardcoded here.
PERFECTIONISM_PARALYSIS_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/perfectionism-paralysis.md"),
    "Activation Signals",
)
PERFECTIONISM_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/shadow-patterns.md"),
    "Perfectionism (as protection)",
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

    # General perfectionism signals add secondary score only. Doctrine
    # (perfectionism-paralysis.md, "Distinguish from genuine discernment"):
    # "Perfectionism paralysis is a pattern, not a single instance." A bare
    # generic phrase must not reach _THRESHOLD alone; it only crosses the
    # threshold combined with the history repetition bonus below, which is
    # the check for "does the pattern appear repeatedly."
    for phrase in PERFECTIONISM_SIGNALS:
        if phrase in msg and score == 0:
            score += 1
            signals.append(f"perfectionism: '{phrase}'")
            break

    # Repetition evidence crosses the "pattern, not a single instance" bar
    # (perfectionism-paralysis.md) either from the current message explicitly
    # naming its own repetition ("a hundred times", "over and over"), or from
    # prior turns naming it.
    repeat_signals = (
        "still not ready",
        "still not finished",
        "still can't",
        "again",
        "still working on",
        "over and over",
        "so many times",
        "every time",
        "a hundred times",
    )
    if score > 0:
        if any(r in msg for r in repeat_signals):
            score += 1
            signals.append("pattern_persistence_in_message")
        elif history:
            hist_text = " ".join(
                m.get("content", "").lower()
                for m in history[-4:]
                if isinstance(m, dict) and m.get("role") == "user"
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
