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
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/emotional-deescalation.md,
# "## Detection signals". Nothing is hardcoded here. (This detector only
# consumes the flooding/pacing/physical groups — the crisis-adjacent groups
# in that file are for crisis_detector's own separate, careful sync pass.)
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
    """
    Returns True if the last 3 user messages show increasing intensity.
    Simple heuristic: message length growing + at least one flooding signal.
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
    """
    Detect emotional overwhelm in the current message.
    Run AFTER crisis_detector  -  only call this if crisis screen returned NONE.

    Returns:
        Dict with: level (str), signals (list), action (str), guidance (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0

    for phrase in PHYSICAL_OVERWHELM:
        if phrase in msg:
            score += 3
            signals_found.append(f"physical: '{phrase}'")

    for phrase in COGNITIVE_FLOODING:
        if phrase in msg:
            score += 2
            signals_found.append(f"cognitive: '{phrase}'")

    for phrase in EMOTIONAL_FLOODING:
        if phrase in msg:
            score += 2
            signals_found.append(f"emotional: '{phrase}'")

    for phrase in PACING_SIGNALS:
        if phrase in msg:
            score += 1
            signals_found.append(f"pacing: '{phrase}'")

    word_count = len(msg.split())
    if word_count > 200:
        score += 1
        signals_found.append(f"length: {word_count} words")

    if msg.count("!") >= 3:
        score += 1
        signals_found.append("punctuation: multiple exclamation marks")

    if history and check_escalation(history):
        score += 2
        signals_found.append("escalation: intensity increasing across messages")

    if score >= 5:
        level = "HIGH"
        action = "DEESCALATE_FULL"
        guidance = (
            "Emotional overwhelm detected. Activate full de-escalation protocol from "
            "skills/frameworks/emotional-deescalation.md. Three steps in order: "
            "(1) Acknowledge intensity  -  simple, direct, no interpretation. "
            "(2) Offer one grounding invitation  -  breath or feet on floor. "
            "(3) Normalize the nervous system response in plain language. "
            "Do NOT use 5-step framework. Do NOT ask a reflective question until grounding is established. "
            "After grounding: bridge gently, then one post-grounding question from deep-inquiry-bank.md."
        )
    elif score >= 2:
        level = "MODERATE"
        action = "SLOW_DOWN"
        guidance = (
            "Moderate emotional activation detected. Slow the conversation down. "
            "Step 1 only: acknowledge the intensity with one warm sentence. "
            "Consider offering a breath invitation if the message has physical signals. "
            "You may continue with a shortened MIRROR response, but hold the framework lightly. "
            "End with a softer question  -  retrieve from 'Post-Grounding Questions' in deep-inquiry-bank.md."
        )
    else:
        level = "NORMAL"
        action = "CONTINUE"
        guidance = (
            "No significant overwhelm detected. Continue standard response pipeline."
        )

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
