"""Classify emotional overwhelm that needs de-escalation first."""

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
    load_key_value_table,
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/emotional-deescalation.md,
# "## Detection signals". Nothing is hardcoded here. (This detector only
# consumes the flooding/pacing/physical groups — the crisis-adjacent groups
# in that file are for crisis_detector's own separate, careful sync pass.)
_RULES = load_key_value_table(
    default_skill_path("skills/frameworks/emotional-deescalation.md"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    default_skill_path("skills/frameworks/emotional-deescalation.md"), "Guidance"
)
_DEESCALATION_GROUPS = load_labeled_groups(
    default_skill_path("skills/frameworks/emotional-deescalation.md"),
    "Detection signals",
)
COGNITIVE_FLOODING = _DEESCALATION_GROUPS["cognitive flooding"]
EMOTIONAL_FLOODING = _DEESCALATION_GROUPS["emotional flooding"]
PACING_SIGNALS = _DEESCALATION_GROUPS["pacing signals"]
INTENSITY_MODIFIERS = _DEESCALATION_GROUPS["intensity modifiers"]
PHYSICAL_OVERWHELM = _DEESCALATION_GROUPS["physical overwhelm"]

HistoryMessage = dict[str, str]


def check_escalation(history: list[HistoryMessage]) -> bool:
    """Report whether the recent user messages show rising intensity.

    A deliberately simple heuristic: message length not shrinking across the
    last three user turns, plus at least one intensity modifier in the most
    recent one.

    Args:
        history: Prior turns, each a dict with ``role`` and ``content``.

    Returns:
        True when both conditions hold. False when fewer than two user
        messages are available to compare.
    """
    user_msgs = [
        m["content"] for m in history if isinstance(m, dict) and m.get("role") == "user"
    ][-3:]

    if len(user_msgs) < 2:
        return False

    lengths = [len(m) for m in user_msgs]
    escalating_length = all(
        lengths[i] <= lengths[i + 1] for i in range(len(lengths) - 1)
    )

    late_msg = user_msgs[-1].lower()
    has_intensity = any(word in late_msg for word in INTENSITY_MODIFIERS)

    return escalating_length and has_intensity


def detect_intensity(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Score emotional overwhelm in the current message.

    Run this only after the crisis screen returns no crisis. Intensity is a
    lower-priority route than crisis, so calling it first would let a crisis
    message be handled as overwhelm.

    Args:
        message: The user's current message.
        history: Prior turns, used to check whether intensity is escalating
            across turns rather than spiking in one.

    Returns:
        A dict with ``level``, ``signals``, ``action``, and ``guidance``.
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0

    for phrase in PHYSICAL_OVERWHELM:
        if phrase in msg:
            score += int(_RULES["Physical overwhelm weight"])
            signals_found.append(f"physical: '{phrase}'")

    for phrase in COGNITIVE_FLOODING:
        if phrase in msg:
            score += int(_RULES["Cognitive flooding weight"])
            signals_found.append(f"cognitive: '{phrase}'")

    for phrase in EMOTIONAL_FLOODING:
        if phrase in msg:
            score += int(_RULES["Emotional flooding weight"])
            signals_found.append(f"emotional: '{phrase}'")

    for phrase in PACING_SIGNALS:
        if phrase in msg:
            score += int(_RULES["Pacing signal weight"])
            signals_found.append(f"pacing: '{phrase}'")

    word_count = len(msg.split())
    if word_count > int(_RULES["Long message word threshold"]):
        score += int(_RULES["Long message weight"])
        signals_found.append(f"length: {word_count} words")

    if msg.count("!") >= int(_RULES["Exclamation threshold"]):
        score += int(_RULES["Exclamation weight"])
        signals_found.append("punctuation: multiple exclamation marks")

    if history and check_escalation(history):
        score += int(_RULES["Escalation weight"])
        signals_found.append("escalation: intensity increasing across messages")

    if score >= int(_RULES["High intensity threshold"]):
        level = "HIGH"
        action = "DEESCALATE_FULL"
        guidance = _GUIDANCE["HIGH"]
    elif score >= int(_RULES["Moderate intensity threshold"]):
        level = "MODERATE"
        action = "SLOW_DOWN"
        guidance = _GUIDANCE["MODERATE"]
    else:
        level = "NORMAL"
        action = "CONTINUE"
        guidance = _GUIDANCE["NORMAL"]

    return {
        "level": level,
        "score": score,
        "signals": signals_found,
        "action": action,
        "guidance": guidance,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_intensity(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
