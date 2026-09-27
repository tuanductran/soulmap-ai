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
    load_key_value_table,
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
_ANCESTRAL_SCORING = load_key_value_table(
    default_skill_path("skills/frameworks/ancestral-patterns.md"), "Scoring"
)
_ANCESTRAL_GUIDANCE = load_key_value_table(
    default_skill_path("skills/frameworks/ancestral-patterns.md"), "Guidance"
)


def detect_ancestral(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect intergenerational/ancestral pattern recognition."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in ANCESTRAL_SIGNALS:
        if phrase in msg:
            score += int(_ANCESTRAL_SCORING["Direct ancestral-signal weight"])
            signals.append(f"ancestral: '{phrase}'")
            break

    # Secondary signals: parent references + pattern language together.
    has_parent = any(signal in msg for signal in PARENT_SIGNALS)
    has_pattern = any(signal in msg for signal in PATTERN_SIGNALS)
    if has_parent and has_pattern and score == 0:
        score += int(
            _ANCESTRAL_SCORING["Parent-reference plus pattern-language weight"]
        )
        signals.append("parent_ref + pattern_language")

    if score < int(_ANCESTRAL_SCORING["Minimum detection score"]):
        return {
            "ancestral_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _ANCESTRAL_GUIDANCE["not_detected"],
        }

    return {
        "ancestral_detected": True,
        "score": score,
        "signals": signals,
        "recommendation": _ANCESTRAL_GUIDANCE["detected"],
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
