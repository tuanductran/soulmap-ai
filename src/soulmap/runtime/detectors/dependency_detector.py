"""Score conversation history for signs of unhealthy AI dependency."""

from __future__ import annotations

import json
import re
import sys

from soulmap.runtime.io.text_normalization import normalize_message_text
from soulmap.runtime.knowledge.keyword_lists import (
    load_key_value_table,
    load_labeled_groups,
    load_table_rows,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_SOURCE = runtime_skill_path("dependency-detection")
_SIGNAL_GROUPS = load_labeled_groups(_SOURCE, "Detection signals")
_DEPENDENCY_KEYWORDS = _SIGNAL_GROUPS["dependency keywords"]
_DECISION_SEEKING = _SIGNAL_GROUPS["decision-seeking phrases"]
_ISOLATION_SIGNALS = _SIGNAL_GROUPS["isolation signals"]

_PATTERN_ROWS = load_table_rows(_SOURCE, "Regex patterns")
_DEPENDENCY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (row[0], re.compile(row[1].strip(chr(96))))
    for row in _PATTERN_ROWS
    if len(row) >= 2
)

_SCORING = load_key_value_table(_SOURCE, "Scoring")
_GUIDANCE = load_key_value_table(_SOURCE, "Guidance")

_DEPENDENCY_KEYWORD_WEIGHT = int(_SCORING["Dependency keyword weight"])
_DEPENDENCY_REGEX_WEIGHT = int(_SCORING["Dependency regex weight"])
_DECISION_SEEKING_WEIGHT = int(_SCORING["Decision-seeking weight"])
_ISOLATION_SIGNAL_WEIGHT = int(_SCORING["Isolation signal weight"])
_HIGH_MESSAGE_VOLUME_THRESHOLD = int(_SCORING["High message volume threshold"])
_HIGH_MESSAGE_VOLUME_BONUS = int(_SCORING["High message volume bonus"])
_HIGH_DEPENDENCY_THRESHOLD = int(_SCORING["High dependency threshold"])
_MODERATE_DEPENDENCY_THRESHOLD = int(_SCORING["Moderate dependency threshold"])


def analyze_dependency(conversation_messages: list) -> dict:
    """Analyze conversation history to detect AI dependency signals.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys.
                               Expected format: [{"role": "user", "content": "..."}]

    Returns:
        Dict with keys: level (str), score (int), signals (list), recommendation (str)
    """
    score = 0
    signals_found = []

    user_messages = [
        normalize_message_text(m["content"])
        for m in conversation_messages
        if isinstance(m, dict) and m.get("role") == "user"
    ]

    if not user_messages:
        return {
            "level": "NO_DATA",
            "score": 0,
            "signals": [],
            "recommendation": "No user messages found in conversation history.",
        }

    for msg in user_messages:
        keyword_match = next(
            (keyword for keyword in _DEPENDENCY_KEYWORDS if keyword in msg),
            None,
        )
        if keyword_match:
            signal = f"dependency_keyword: '{keyword_match}'"
            if signal not in signals_found:
                score += _DEPENDENCY_KEYWORD_WEIGHT
                signals_found.append(signal)
            continue

        for label, pattern in _DEPENDENCY_PATTERNS:
            if pattern.search(msg):
                signal = f"dependency_pattern: '{label}'"
                if signal not in signals_found:
                    score += _DEPENDENCY_REGEX_WEIGHT
                    signals_found.append(signal)
                break

    decision_count = 0
    for msg in user_messages:
        for pattern in _DECISION_SEEKING:
            if pattern in msg:
                decision_count += 1
                score += _DECISION_SEEKING_WEIGHT
    if decision_count > 0:
        signals_found.append(f"decision_seeking_count: {decision_count}")

    for msg in user_messages:
        for signal in _ISOLATION_SIGNALS:
            if signal in msg:
                score += _ISOLATION_SIGNAL_WEIGHT
                if signal not in signals_found:
                    signals_found.append(f"isolation_signal: '{signal}'")

    if len(user_messages) > _HIGH_MESSAGE_VOLUME_THRESHOLD:
        score += _HIGH_MESSAGE_VOLUME_BONUS
        signals_found.append(f"high_message_volume: {len(user_messages)} user messages")

    if score >= _HIGH_DEPENDENCY_THRESHOLD:
        level = "HIGH_DEPENDENCY"
    elif score >= _MODERATE_DEPENDENCY_THRESHOLD:
        level = "MODERATE_DEPENDENCY"
    else:
        level = "LOW_DEPENDENCY"

    return {
        "level": level,
        "score": score,
        "signals": signals_found,
        "recommendation": _GUIDANCE[level],
    }


if __name__ == "__main__":
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            print(
                json.dumps(
                    {
                        "level": "NO_DATA",
                        "score": 0,
                        "signals": [],
                        "recommendation": "No input provided.",
                    }
                )
            )
            sys.exit(0)

        data = json.loads(raw)
        messages = data if isinstance(data, list) else data.get("messages", [])
        result = analyze_dependency(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(json.dumps({"level": "ERROR", "error": f"JSON parse error: {e!s}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"level": "ERROR", "error": str(e)}))
        sys.exit(1)
