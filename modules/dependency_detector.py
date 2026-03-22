"""Score conversation history for signs of unhealthy AI dependency."""

import json
import re
import sys

from modules.config import (
    DECISION_SEEKING,
    DEPENDENCY_KEYWORDS,
    HIGH_DEPENDENCY_THRESHOLD,
    ISOLATION_SIGNALS,
    MODERATE_DEPENDENCY_THRESHOLD,
)
from modules.text_normalization import normalize_message_text

DEPENDENCY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "only you understand me",
        re.compile(r"\bonly you\s+(?:really\s+|truly\s+)?understand(?:s)?\s+me\b"),
    ),
    (
        "you are the only one who understands me",
        re.compile(
            r"\byou(?:'re| are)\s+the\s+only\s+one\s+who\s+"
            r"(?:really\s+|truly\s+)?understands\s+me\b"
        ),
    ),
]


def analyze_dependency(conversation_messages: list) -> dict:
    """
    Analyze conversation history to detect AI dependency signals.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys.
                               Expected format: [{"role": "user", "content": "..."}, ...]

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
            (keyword for keyword in DEPENDENCY_KEYWORDS if keyword in msg),
            None,
        )
        if keyword_match:
            signal = f"dependency_keyword: '{keyword_match}'"
            if signal not in signals_found:
                score += 2
                signals_found.append(signal)
            continue

        for label, pattern in DEPENDENCY_PATTERNS:
            if pattern.search(msg):
                signal = f"dependency_pattern: '{label}'"
                if signal not in signals_found:
                    score += 2
                    signals_found.append(signal)
                break

    decision_count = 0
    for msg in user_messages:
        for pattern in DECISION_SEEKING:
            if pattern in msg:
                decision_count += 1
                score += 1
    if decision_count > 0:
        signals_found.append(f"decision_seeking_count: {decision_count}")

    for msg in user_messages:
        for signal in ISOLATION_SIGNALS:
            if signal in msg:
                score += 2
                if signal not in signals_found:
                    signals_found.append(f"isolation_signal: '{signal}'")

    if len(user_messages) > 10:
        score += 1
        signals_found.append(f"high_message_volume: {len(user_messages)} user messages")

    if score >= HIGH_DEPENDENCY_THRESHOLD:
        level = "HIGH_DEPENDENCY"
        recommendation = (
            "Warmly redirect toward real-world support. Use the dependency detection "
            "response: 'I notice you have been returning here often for decisions like "
            "this. The answers you are searching for live in you, not in our conversations. "
            "Is there someone in your real life you could bring this to?'"
        )
    elif score >= MODERATE_DEPENDENCY_THRESHOLD:
        level = "MODERATE_DEPENDENCY"
        recommendation = (
            "Begin gently pointing back to the user's own knowing. Celebrate any signs "
            "of self-direction. Avoid becoming the primary decision-making source."
        )
    else:
        level = "LOW_DEPENDENCY"
        recommendation = "No significant dependency signals detected. Continue normal reflective engagement."

    return {
        "level": level,
        "score": score,
        "signals": signals_found,
        "recommendation": recommendation,
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
        if isinstance(data, list):
            messages = data
        else:
            messages = data.get("messages", [])
        result = analyze_dependency(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(json.dumps({"level": "ERROR", "error": f"JSON parse error: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"level": "ERROR", "error": str(e)}))
        sys.exit(1)
