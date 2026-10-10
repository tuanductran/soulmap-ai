"""Detect empath boundary dissolution and energetic overwhelm (P8d)."""

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

# Single source of truth: skills/frameworks/empath-boundary/content/empath-boundary.md,
# "## Activation Signals". Nothing is hardcoded here.
EMPATH_SIGNALS = load_keyword_section(
    runtime_skill_path("empath-boundary"), "Activation Signals"
)
_RULES = load_key_value_table(
    runtime_skill_path("empath-boundary"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(runtime_skill_path("empath-boundary"), "Guidance")


HistoryMessage = dict[str, str]


def detect_empath_overwhelm(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect empath boundary dissolution and absorption of others' emotions."""
    msg = message.lower().strip()
    signals: list[str] = []
    score = 0

    for phrase in EMPATH_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Activation signal weight"])
            signals.append(f"empath: '{phrase}'")
            break

    # Secondary: drain/exhaustion + people/others context
    drain = load_keyword_section(runtime_skill_path("empath-boundary"), "Drain signals")
    people_ctx = load_keyword_section(
        runtime_skill_path("empath-boundary"),
        "People-context signals",
    )
    if (
        any(d in msg for d in drain)
        and any(p in msg for p in people_ctx)
        and score == 0
    ):
        score += int(_RULES["Drain plus people-context weight"])
        signals.append("drain + people context")

    if score < int(_RULES["Minimum detection score"]):
        return {
            "empath_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "empath_detected": True,
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
                detect_empath_overwhelm(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
