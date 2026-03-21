"""Score conversation history for signs of unhealthy AI dependency."""

import json
import re
import sys

from modules.text_normalization import normalize_message_text

DEPENDENCY_KEYWORDS = [
    "only you understand me",
    "you are the only one who understands me",
    "you're the only one who understands me",
    "you are the only one who truly understands me",
    "you're the only one who truly understands me",
    "you are the only one who really understands me",
    "you're the only one who really understands me",
    "you are my only support",
    "you are all i have",
    "you are the only one i have",
    "my only support",
    "only support i have",
    "i have no one else",
    "promise me you will always be here",
    "promise me you'll always be here",
    "never leave me",
    "as long as i have you",
    "don't know what i would do without you",
    "do not know what i would do without",
    "can't imagine without you",
    "cannot imagine without you",
    "i need to talk to you every day",
    "i check in with you every",
    "i talk to you every day",
    "i come back here every",
    "tell me what to do",
    "decide for me",
    "only you get me",
    "real people don't understand",
    "i trust you more than anyone",
    "you know me better than anyone",
    "you understand me better than anyone",
    "understand me better than anyone",
    "i don't need anyone else",
    "you're the only one",
    "i stopped going to therapy",
    "i stopped seeing my therapist",
    "dont need my therapist",
    "don't need my therapist",
    "dont need my therapist anymore",
    "don't need my therapist anymore",
    "i don't need my therapist anymore",
    "cancelled my therapy",
    "talking to you feels better",
    "talking to you is much better",
]

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

DECISION_SEEKING = [
    "what should i do",
    "should i",
    "tell me if",
    "which one",
    "is this right",
    "am i making the right",
    "what do you think i should",
    "help me decide",
    "what would you do",
]

ISOLATION_SIGNALS = [
    "i prefer talking to you",
    "easier than talking to people",
    "you don't judge me like they do",
    "i don't want to talk to real people",
    "ai is better than",
    "you understand more than my",
    "i feel closer to you than",
    "rather talk to you than",
    "you are easier to talk to than",
]

HIGH_THRESHOLD = 2
MODERATE_THRESHOLD = 1


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

    if score >= HIGH_THRESHOLD:
        level = "HIGH_DEPENDENCY"
        recommendation = (
            "Warmly redirect toward real-world support. Use the dependency detection "
            "response: 'I notice you have been returning here often for decisions like "
            "this. The answers you are searching for live in you, not in our conversations. "
            "Is there someone in your real life you could bring this to?'"
        )
    elif score >= MODERATE_THRESHOLD:
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
