"""Detect inner conflict and likely competing parts in user language."""

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

# Single source of truth: skills/frameworks/inner-parts.md,
# "## Detection signals". Nothing is hardcoded here.
_INNER_PARTS_GROUPS = load_labeled_groups(
    runtime_skill_path("inner-parts"), "Detection signals"
)
EXPLICIT_CONFLICT = _INNER_PARTS_GROUPS["explicit inner conflict"]
PART_NAMING = _INNER_PARTS_GROUPS["part-naming"]
BEHAVIORAL_CONFUSION = _INNER_PARTS_GROUPS["behavioral confusion"]
_RULES = load_key_value_table(
    runtime_skill_path("inner-parts"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(
    runtime_skill_path("inner-parts"),
    "Guidance",
)

SELF_DIALOGUE = _INNER_PARTS_GROUPS["internal dialogue"]

HistoryMessage = dict[str, str]


def detect_inner_conflict(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Detect inner conflict signals in the current message and recent history.

    Args:
        message: The current user message.
        history: Full conversation history (optional).

    Returns:
        Dict with: conflict_detected (bool), type (str), signals (list),
                   parts_suggested (list), recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    conflict_types = []

    for phrase in EXPLICIT_CONFLICT:
        if phrase in msg:
            score += int(_RULES["Explicit-conflict weight"])
            signals_found.append(f"explicit: '{phrase}'")
            if "explicit" not in conflict_types:
                conflict_types.append("explicit")

    for phrase in SELF_DIALOGUE:
        if phrase in msg:
            score += int(_RULES["Self-dialogue weight"])
            signals_found.append(f"self_dialogue: '{phrase}'")
            if "self_dialogue" not in conflict_types:
                conflict_types.append("self_dialogue")

    for phrase in PART_NAMING:
        if phrase in msg:
            score += int(_RULES["Part-naming weight"])
            signals_found.append(f"part_naming: '{phrase}'")
            if "part_naming" not in conflict_types:
                conflict_types.append("part_naming")

    for phrase in BEHAVIORAL_CONFUSION:
        if phrase in msg:
            score += int(_RULES["Behavioral-confusion weight"])
            signals_found.append(f"confusion: '{phrase}'")
            if "behavioral_confusion" not in conflict_types:
                conflict_types.append("behavioral_confusion")

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-int(_RULES["History window"]) :]
        for past_msg in recent_user:
            for phrase in EXPLICIT_CONFLICT[
                : int(_RULES["Historical signal limit"])
            ]:  # Check strongest signals in history
                if phrase in past_msg:
                    score += int(_RULES["Historical explicit-conflict bonus"])
                    if "historical" not in conflict_types:
                        conflict_types.append("historical")
                    break

    parts_suggested = _suggest_parts(msg)

    conflict_detected = score >= int(_RULES["Minimum detection score"])

    if not conflict_detected:
        return {
            "conflict_detected": False,
            "type": None,
            "score": score,
            "signals": signals_found,
            "parts_suggested": [],
            "recommendation": _GUIDANCE["not_detected"],
        }

    primary_type = conflict_types[0] if conflict_types else "general"

    recommendation = _GUIDANCE["detected"].format(primary_type=primary_type)

    if parts_suggested:
        recommendation += " " + _GUIDANCE["detected_parts_suffix"].format(
            parts=", ".join(parts_suggested)
        )

    return {
        "conflict_detected": True,
        "type": primary_type,
        "score": score,
        "signals": signals_found,
        "parts_suggested": parts_suggested,
        "recommendation": recommendation,
    }


def _suggest_parts(msg: str) -> list[str]:
    """Suggest part archetypes using the Markdown-owned signal groups.

    Args:
        msg: The user's current message, already lowercased and stripped.

    Returns:
        Up to three archetype names whose authored signals match the message.
    """
    archetype_labels = (
        ("protective part", "protective part"),
        ("fearful part", "fearful part"),
        ("hopeful part", "hopeful part"),
        ("tired part", "tired part"),
        ("angry part", "angry part"),
        ("critical part", "critical part"),
        ("yearning part", "yearning part"),
        ("avoidant part", "avoidant part"),
    )
    suggestions = [
        part_name
        for group_name, part_name in archetype_labels
        if any(signal in msg for signal in _INNER_PARTS_GROUPS.get(group_name, ()))
    ]
    return suggestions[:3]


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_inner_conflict(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
