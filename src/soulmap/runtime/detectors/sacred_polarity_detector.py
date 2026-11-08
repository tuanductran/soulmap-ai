"""Detect sacred feminine/masculine polarity reflection: receptivity vs action balance."""

from __future__ import annotations

import json
import re
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

_NEGATED_POLARITY_FRAME = re.compile(
    r"\\b(?:don't|do not|never|can't|cannot)\\s+(?:really\\s+)?"
    r"(?:relate to|identify with|resonate with|believe in|use|subscribe to|"
    r"feel connected to)\\s+(?:the\\s+)?$",
    re.IGNORECASE,
)


def _is_quoted_span(text: str, start: int, end: int) -> bool:
    """Return whether a framing phrase is enclosed in quotation marks."""
    for opening, closing in (('"', '"'), ("“", "”"), ("‘", "’")):
        quote_start = text.rfind(opening, 0, start + 1)
        quote_end = text.find(closing, end)
        if quote_start < 0 or quote_end < 0:
            continue
        if text.find(closing, quote_start + len(opening), start) < 0:
            return True
    return False


def _has_explicit_polarity_frame(text: str) -> bool:
    """Require an affirmative, unquoted user-authored polarity frame."""
    for phrase in POLARITY_FRAMING_SIGNALS:
        for match in re.finditer(re.escape(phrase), text, re.IGNORECASE):
            if _is_quoted_span(text, match.start(), match.end()):
                continue
            prefix = text[max(0, match.start() - 100) : match.start()]
            if _NEGATED_POLARITY_FRAME.search(prefix):
                continue
            return True
    return False


def detect_sacred_polarity(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect the user exploring balance of receptivity and action, surrender and will."""
    msg = message.lower().strip()
    user_texts = [
        item.get("content", "")
        for item in (history or [])
        if isinstance(item, dict) and item.get("role") == "user"
    ]
    user_texts.append(message)
    has_user_polarity_frame = any(
        _has_explicit_polarity_frame(text) for text in user_texts
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
