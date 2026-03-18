"""Score conversation history for signs of unhealthy AI dependency."""

import json
import sys

DEPENDENCY_KEYWORDS = [
    "only you understand me",
    "can't imagine without you",
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
    "dont need my therapist",
    "don't need my therapist",
    "cancelled my therapy",
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
]

HIGH_THRESHOLD = 6
MODERATE_THRESHOLD = 3


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
        m["content"].lower()
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
        for keyword in DEPENDENCY_KEYWORDS:
            if keyword in msg:
                score += 2
                if keyword not in signals_found:
                    signals_found.append(f"dependency_keyword: '{keyword}'")

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
