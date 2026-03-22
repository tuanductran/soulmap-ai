"""Detect existential territory that needs holding rather than solving."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from modules.config import (
    ENDINGS_GRIEF,
    HOLDING_QUESTIONS,
    IDENTITY_SHIFT,
    LARGER_QUESTIONS,
    MEANING_DEPTH,
)

HistoryMessage = dict[str, str]


def _classify_territory(_msg: str, scores: dict[str, int]) -> str:
    """Return the primary existential territory."""
    territory_scores = {
        "identity_shift": scores.get("identity_shift", 0),
        "meaning_depth": scores.get("meaning_depth", 0),
        "endings_grief": scores.get("endings_grief", 0),
        "larger_questions": scores.get("larger_questions", 0),
        "holding": scores.get("holding", 0),
    }
    primary = max(territory_scores, key=lambda territory: territory_scores[territory])
    if territory_scores[primary] == 0:
        return "general"
    return primary


def detect_existential(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """
    Detect existential territory in the user's message.

    Returns:
        Dict with: existential_detected (bool), territory (str), score (int),
                   signals (list), recommendation (str)
    """
    msg = message.lower().strip()
    signals_found = []
    score = 0
    territory_scores = {
        "identity_shift": 0,
        "meaning_depth": 0,
        "endings_grief": 0,
        "larger_questions": 0,
        "holding": 0,
    }

    signal_map = [
        ("identity_shift", IDENTITY_SHIFT, 3),
        ("meaning_depth", MEANING_DEPTH, 3),
        ("endings_grief", ENDINGS_GRIEF, 3),
        ("larger_questions", LARGER_QUESTIONS, 3),
        ("holding", HOLDING_QUESTIONS, 2),
    ]

    for territory, signals, weight in signal_map:
        for phrase in signals:
            if phrase in msg:
                score += weight
                territory_scores[territory] += weight
                signals_found.append(f"{territory}: '{phrase}'")
                break  # one match per territory per pass

    if history:
        recent_user = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-4:]
        returning_signals = (
            IDENTITY_SHIFT[:6]
            + MEANING_DEPTH[:6]
            + ENDINGS_GRIEF[:4]
            + LARGER_QUESTIONS[:4]
        )
        count = sum(
            1
            for past in recent_user
            if any(phrase in past for phrase in returning_signals)
        )
        if count >= 2:
            score += 2
            signals_found.append(
                "sustained: existential territory across multiple messages"
            )

    if score < 2:
        return {
            "existential_detected": False,
            "territory": None,
            "score": score,
            "signals": signals_found,
            "recommendation": "No existential signals detected. Continue standard pipeline.",
        }

    territory = _classify_territory(msg, territory_scores)

    territory_guidance = {
        "identity_shift": (
            "Identity shift territory. "
            "Do not help them reconstruct a new identity. "
            "Stay with the in-between: 'Being between versions of yourself is a real place  -  not a state to fix.' "
            "Reflect the disorientation without resolving it."
        ),
        "meaning_depth": (
            "Meaning-at-depth territory. "
            "Do not provide meaning or suggest where it might be found. "
            "Let the absence be real: 'The absence of meaning is its own weight  -  not sadness exactly, but more like a hollow.' "
            "The question is for inhabiting, not answering."
        ),
        "endings_grief": (
            "Endings and grief territory. "
            "Honor the ending as real. No silver linings. "
            "Endings are allowed to be just endings: 'Endings carry their own grief  -  even when what's ending needed to end.'"
        ),
        "larger_questions": (
            "Larger questions territory (mortality, impermanence, cosmic scale). "
            "Do not make it smaller or more manageable. "
            "Let it be as large as it is: 'These are the questions that don't resolve  -  they just get bigger.'"
        ),
        "holding": (
            "User is sitting with a question  -  they already know it has no answer. "
            "Be honest: 'I don't have an answer  -  and I think that's honest.' "
            "Sit alongside the question with them."
        ),
        "general": (
            "General existential territory. "
            "Use holding-space language from skills/frameworks/existential-companion.md. "
            "Reflect without reducing. Stay with the weight."
        ),
    }

    recommendation = (
        f"Existential territory detected (territory: {territory}). "
        "Activate Existential Reflection Companion from skills/frameworks/existential-companion.md. "
        + territory_guidance.get(territory, territory_guidance["general"])
        + " Do NOT provide philosophical conclusions. Do NOT resolve the uncertainty. "
        "Do NOT use growth narrative or silver linings. "
        "Hold space. End with one question that goes deeper into the exploration. "
        "Retrieve from skills/meta/deep-inquiry-bank.md  -  'Existential Questions' section."
    )

    return {
        "existential_detected": True,
        "territory": territory,
        "score": score,
        "signals": signals_found,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_existential(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
