"""Detect grief signals that should override standard reflection."""

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
    load_labeled_groups,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/grief-companion.md,
# "## Detection signals". Nothing is hardcoded here.
_GRIEF_GROUPS = load_labeled_groups(
    runtime_skill_path("grief-companion"), "Detection signals"
)
_RULES = load_key_value_table(
    runtime_skill_path("grief-companion"),
    "Runtime detection contract",
)
_GRIEF_TYPES = load_key_value_table(
    runtime_skill_path("grief-companion"), "Detection type mapping"
)
_GUIDANCE = load_key_value_table(runtime_skill_path("grief-companion"), "Guidance")
ACUTE_GRIEF = _GRIEF_GROUPS["acute grief"]
ANTICIPATORY_GRIEF = _GRIEF_GROUPS["anticipatory grief"]
AMBIGUOUS_LOSS = _GRIEF_GROUPS["ambiguous loss"]
COMPLICATED_GRIEF = _GRIEF_GROUPS["complicated grief"]

HistoryMessage = dict[str, str]


def detect_grief(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Score grief signals in the current message.

    Matches the phrase groups authored in
    ``skills/frameworks/grief-companion.md``: acute grief, anticipatory grief,
    ambiguous loss, and complicated grief. Acute grief is checked first, since
    it routes to the shortest and most held response.

    Args:
        message: The user's current message.
        history: Prior turns. Accepted for a uniform detector signature and
            not used, since grief is read from the current message.

    Returns:
        A dict with ``grief_detected``, ``grief_type``, ``score``,
        ``signals``, and ``recommendation``.
    """
    msg = message.lower().strip()
    signals = []
    score = 0
    grief_type = None

    for phrase in ACUTE_GRIEF:
        if phrase in msg:
            score += int(_RULES["Acute grief weight"])
            signals.append(f"acute: '{phrase}'")
            grief_type = _GRIEF_TYPES["acute grief"]
            break

    for phrase in ANTICIPATORY_GRIEF:
        if phrase in msg:
            score += int(_RULES["Anticipatory grief weight"])
            signals.append(f"anticipatory: '{phrase}'")
            if not grief_type:
                grief_type = _GRIEF_TYPES["anticipatory grief"]
            break

    for phrase in AMBIGUOUS_LOSS:
        if phrase in msg:
            score += int(_RULES["Ambiguous loss weight"])
            signals.append(f"ambiguous: '{phrase}'")
            if not grief_type:
                grief_type = _GRIEF_TYPES["ambiguous loss"]
            break

    for phrase in COMPLICATED_GRIEF:
        if phrase in msg:
            score += int(_RULES["Complicated grief weight"])
            signals.append(f"complicated: '{phrase}'")
            if not grief_type:
                grief_type = _GRIEF_TYPES["complicated grief"]
            break

    if history:
        recent = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-int(_RULES["Recent user history window"]) :]
        all_grief = (
            ACUTE_GRIEF[: int(_RULES["Acute history signal limit"])]
            + ANTICIPATORY_GRIEF[: int(_RULES["Anticipatory history signal limit"])]
            + AMBIGUOUS_LOSS[: int(_RULES["Ambiguous history signal limit"])]
        )
        if sum(1 for m in recent if any(p in m for p in all_grief)) >= 2:
            score += int(_RULES["Sustained grief weight"])
            signals.append("sustained_grief_across_messages")

    if score < int(_RULES["Minimum detection score"]):
        return {
            "grief_detected": False,
            "grief_type": None,
            "score": score,
            "signals": [],
        }

    detected_type = grief_type or _GRIEF_TYPES["acute grief"]
    recommendation = (
        _GUIDANCE["detected_prefix"].format(
            grief_type=detected_type,
            guidance=_GUIDANCE.get(detected_type, ""),
        )
        + " "
        + _GUIDANCE["detected_suffix"]
    )

    return {
        "grief_detected": True,
        "grief_type": detected_type,
        "score": score,
        "signals": signals,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        result = detect_grief(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
