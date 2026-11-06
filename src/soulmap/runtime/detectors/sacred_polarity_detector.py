"""Detect sacred feminine/masculine polarity reflection: receptivity vs action balance."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from soulmap.runtime.knowledge.keyword_lists import (
    load_keyword_section,
    load_runtime_guidance,
)
from soulmap.runtime.knowledge.runtime_config import DETECTOR_CONFIG
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/sacred-feminine-masculine.md,
# "## Activation Signals". Nothing is hardcoded here.
SACRED_POLARITY_SIGNALS = load_keyword_section(
    runtime_skill_path("sacred-feminine-masculine"),
    "Activation Signals",
)
POLARITY_FRAMING_SIGNALS = load_keyword_section(
    runtime_skill_path("sacred-feminine-masculine"),
    "Explicit Polarity Framing",
)
_RULES = DETECTOR_CONFIG["sacred_polarity"]
_GUIDANCE = load_runtime_guidance(
    runtime_skill_path("sacred-feminine-masculine"),
    "Guidance",
)

HistoryMessage = dict[str, str]


def detect_sacred_polarity(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user exploring balance of receptivity and action, surrender and will."""
    msg = message.lower().strip()
    prior_user_text = " ".join(
        item.get("content", "").lower()
        for item in (history or [])
        if isinstance(item, dict) and item.get("role") == "user"
    )
    framing_context = f"{prior_user_text} {msg}"
    has_user_polarity_frame = any(
        phrase in framing_context for phrase in POLARITY_FRAMING_SIGNALS
    )
    signals: list[str] = []
    score = 0

    if has_user_polarity_frame:
        for phrase in SACRED_POLARITY_SIGNALS:
            if phrase in msg:
                score += int(_RULES["Activation signal weight"])
                signals.append(f"sacred_polarity: '{phrase}'")
                break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "sacred_polarity_detected": False,
            "score": score,
            "signals": signals,
            "recommendation": _GUIDANCE["not_detected"],
        }

    return {
        "sacred_polarity_detected": True,
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
                detect_sacred_polarity(message, history), ensure_ascii=False, indent=2
            )
        )
    except (ValueError, Exception) as e:
        print_json_error(e)
        sys.exit(1)
