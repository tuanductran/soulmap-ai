"""Classify emotional overwhelm that needs de-escalation first."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

PHYSICAL_OVERWHELM = [
    "my heart is racing",
    "heart racing",
    "can't breathe properly",
    "can't breathe",
    "shaking",
    "i'm shaking",
    "feel sick",
    "feeling sick",
    "my chest is tight",
    "chest tightness",
    "feel dizzy",
    "feeling dizzy",
    "hands are shaking",
    "head is spinning",
    "my head is spinning",
    "stomach is in knots",
]

COGNITIVE_FLOODING = [
    "i can't think",
    "can't think straight",
    "my head is spinning",
    "head is spinning",
    "i don't even know where to start",
    "don't know where to start",
    "i'm all over the place",
    "all over the place",
    "can't focus",
    "my thoughts are everywhere",
    "thoughts are everywhere",
    "can't make sense of anything",
    "everything is happening at once",
    "too much at once",
    "overwhelmed by everything",
    "i don't know what i'm feeling",
    "don't know what i feel",
]

EMOTIONAL_FLOODING = [
    "i'm angry and sad and",
    "angry and scared",
    "i don't know if i'm angry or",
    "crying and angry",
    "laughing and crying",
    "i'm so confused and",
    "everything feels",
    "i feel everything",
    "i feel nothing and everything",
    "i'm a mess",
    "complete mess",
    "total mess right now",
    "i can't stop crying",
    "been crying all day",
    "won't stop crying",
    "i'm spiraling",
    "spiraling right now",
    "going in circles",
]

PACING_SIGNALS = [
    "i don't even know",
    "i just don't know",
    "i honestly don't know",
    "i don't know i don't know",
    "everything is just",
    "and then and then",
    "but also but also",
]


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
    intensity_words = [
        "i can't",
        "everything",
        "nothing",
        "always",
        "never",
        "all of it",
    ]
    has_intensity = any(w in late_msg for w in intensity_words)

    return escalating_length and has_intensity


def detect_intensity(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect emotional overwhelm in the current message.
    Run AFTER crisis_detector — only call this if crisis screen returned NONE.

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
            "(1) Acknowledge intensity — simple, direct, no interpretation. "
            "(2) Offer one grounding invitation — breath or feet on floor. "
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
            "End with a softer question — retrieve from 'Post-Grounding Questions' in deep-inquiry-bank.md."
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
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        history = require_list_field(data, "history")

        if not message:
            print(json.dumps({"error": "No 'message' field in input."}))
            sys.exit(1)

        result = detect_intensity(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
