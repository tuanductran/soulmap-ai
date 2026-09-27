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
    load_key_value_table,
    load_keyword_section,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/perfectionism-paralysis.md and
# skills/frameworks/shadow-patterns.md. Nothing is hardcoded here.
PERFECTIONISM_PARALYSIS_SIGNALS = load_keyword_section(
    runtime_skill_path("perfectionism-paralysis"),
    "Activation Signals",
)
PERFECTIONISM_SIGNALS = load_keyword_section(
    runtime_skill_path("shadow-patterns"),
    "Perfectionism (as protection)",
)
_RULES = load_key_value_table(
    runtime_skill_path("perfectionism-paralysis"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    runtime_skill_path("perfectionism-paralysis"),
    "Guidance",
)
PERSISTENCE_SIGNALS = load_keyword_section(
    runtime_skill_path("perfectionism-paralysis"),
    "Persistence signal group",
)


HistoryMessage = dict[str, str]


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
            score += int(_RULES["Paralysis signal weight"])
            signals.append(f"paralysis: '{phrase}'")
            break

    # General perfectionism signals add secondary score only. Doctrine
    # (perfectionism-paralysis.md, "Distinguish from genuine discernment"):
    # "Perfectionism paralysis is a pattern, not a single instance." A bare
    # generic phrase must not reach the minimum detection score alone; it only crosses the
    # threshold combined with the history repetition bonus below, which is
    # the check for "does the pattern appear repeatedly."
    for phrase in PERFECTIONISM_SIGNALS:
        if phrase in msg and score == 0:
            score += int(_RULES["General perfectionism weight"])
            signals.append(f"perfectionism: '{phrase}'")
            break

    # Repetition evidence crosses the "pattern, not a single instance" bar
    # (perfectionism-paralysis.md) either from the current message explicitly
    # naming its own repetition ("a hundred times", "over and over"), or from
    # prior turns naming it.
    repeat_signals = PERSISTENCE_SIGNALS
    if score > 0:
        if any(r in msg for r in repeat_signals):
            score += int(_RULES["Persistence bonus"])
            signals.append("pattern_persistence_in_message")
        elif history:
            hist_text = " ".join(
                m.get("content", "").lower()
                for m in history[-int(_RULES["History window"]) :]
                if isinstance(m, dict) and m.get("role") == "user"
            )
            if any(r in hist_text for r in repeat_signals):
                score += int(_RULES["Persistence bonus"])
                signals.append("pattern_persistence_in_history")

    if score < int(_RULES["Minimum detection score"]):
        return {
            "perfectionism_paralysis_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "perfectionism_paralysis_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": _GUIDANCE["detected"],
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
