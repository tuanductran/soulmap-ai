"""Detect recurring self-described patterns across conversation history."""

from __future__ import annotations

import json
import sys
from typing import cast

from soulmap.runtime.io.cli_payload import print_json_error, read_stdin_json_value
from soulmap.runtime.knowledge.keyword_lists import load_key_value_table
from soulmap.runtime.knowledge.pattern_source import load_pattern_signals
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/pattern-mapper.md.
# Nothing about a pattern (name, description, detection keywords, cycle
# phrases, SoulMap role guidance, reflection language) is hardcoded here —
# it is parsed from the Markdown skill so the two can never drift apart.
PATTERN_SIGNALS = load_pattern_signals(runtime_skill_path("pattern-mapper"))
_PATTERN_RULES = load_key_value_table(runtime_skill_path("pattern-mapper"), "Scoring")
_PATTERN_GUIDANCE = load_key_value_table(
    runtime_skill_path("pattern-mapper"), "Runtime guidance"
)


def detect_patterns(conversation_messages: list) -> dict:
    """Analyze conversation history to detect psychological/behavioral patterns.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys.

    Returns:
        Dict with: patterns_detected (list), primary_pattern (str|None),
                   combination (bool), recommendation (str), wait_for_more (bool)
    """
    user_messages = [
        m["content"].lower()
        for m in conversation_messages
        if isinstance(m, dict) and m.get("role") == "user"
    ]

    if len(user_messages) < int(_PATTERN_RULES["Minimum user messages"]):
        return {
            "patterns_detected": [],
            "primary_pattern": None,
            "combination": False,
            "wait_for_more": True,
            "recommendation": _PATTERN_GUIDANCE["insufficient_history"],
        }

    scores = dict.fromkeys(PATTERN_SIGNALS, 0)
    signals_found = {pattern: [] for pattern in PATTERN_SIGNALS}

    full_text = " ".join(user_messages)

    for pattern_id, data in PATTERN_SIGNALS.items():
        for kw in data.keywords:
            if kw in full_text:
                scores[pattern_id] += int(_PATTERN_RULES["Keyword signal weight"])
                if kw not in signals_found[pattern_id]:
                    signals_found[pattern_id].append(kw)

        for phrase in data.cycle_phrases:
            if phrase in full_text:
                scores[pattern_id] += int(_PATTERN_RULES["Cycle phrase weight"])
                if phrase not in signals_found[pattern_id]:
                    signals_found[pattern_id].append(f"[cycle] {phrase}")

    detected = [
        {
            "pattern": pid,
            "name": PATTERN_SIGNALS[pid].name,
            "score": scores[pid],
            "signals": signals_found[pid],
            "reflection_en": PATTERN_SIGNALS[pid].reflection_language[0],
            "soulmap_role": PATTERN_SIGNALS[pid].soulmap_role,
        }
        for pid in scores
        if scores[pid] >= int(_PATTERN_RULES["Minimum pattern score"])
    ]

    detected.sort(key=lambda x: -x["score"])

    primary = detected[0]["pattern"] if detected else None
    combination = len(detected) >= int(_PATTERN_RULES["Combination threshold"])

    if not detected:
        recommendation = _PATTERN_GUIDANCE["not_detected"]
    elif combination:
        recommendation = _PATTERN_GUIDANCE["combination"]
    else:
        recommendation = _PATTERN_GUIDANCE["detected"]

    return {
        "patterns_detected": detected,
        "primary_pattern": primary,
        "combination": combination,
        "wait_for_more": False,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json_value(strip=True)
        if isinstance(data, list):
            messages = cast(list, data)
        else:
            messages = cast(list, data.get("messages", []))
        result = detect_patterns(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
