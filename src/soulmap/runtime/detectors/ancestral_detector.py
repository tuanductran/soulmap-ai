"""Detect intergenerational and ancestral pattern recognition signals (P8b)."""

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
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/ancestral-patterns.md,
# "## Activation Signals" and "## Detection signals". Nothing is hardcoded here.
ANCESTRAL_SIGNALS = load_keyword_section(
    default_skill_path("skills/frameworks/ancestral-patterns.md"), "Activation Signals"
)
_ANCESTRAL_GROUPS = load_labeled_groups(
    default_skill_path("skills/frameworks/ancestral-patterns.md"), "Detection signals"
)
PARENT_SIGNALS = _ANCESTRAL_GROUPS["parent references"]
PATTERN_SIGNALS = _ANCESTRAL_GROUPS["pattern language"]

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

    # Secondary signals: parent references + pattern language together.
    has_parent = any(signal in msg for signal in PARENT_SIGNALS)
    has_pattern = any(signal in msg for signal in PATTERN_SIGNALS)
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
