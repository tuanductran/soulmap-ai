"""Detect positive emotional states that call for the Integration and Celebration framework (P9b)."""

from __future__ import annotations

import json
import sys

from soulmap_runtime.config import (
    CELEBRATION_GRATITUDE,
    CELEBRATION_PROGRESS,
    CELEBRATION_RELIEF,
    CELEBRATION_WIN,
)
from soulmap_runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]

# Signal weights
_WIN_SCORE = 3
_RELIEF_SCORE = 3
_GRATITUDE_SCORE = 2
_PROGRESS_SCORE = 2

# Minimum score to activate the framework
_THRESHOLD = 2

# Negative override signals - these indicate the positive state is mixed with pain;
# higher-priority frameworks (grief, crisis, shadow) will handle those cases.
_NEGATIVE_OVERRIDES: tuple[str, ...] = (
    "but i'm still",
    "but i am still",
    "but it still hurts",
    "but i feel empty",
    "but i still feel empty",
    "still feel empty",
    "it doesn't feel real",
    "i don't deserve",
    "i do not deserve",
    "i shouldn't feel happy",
    "i should not feel happy",
    "why don't i feel",
    "why do not i feel",
    "something is wrong with me",
    "can't enjoy it",
    "cannot enjoy it",
)


def _classify_celebration_type(msg: str) -> str:
    """Identify the primary subtype of the positive state."""
    if any(p in msg for p in CELEBRATION_PROGRESS):
        return "recognized_progress"
    if any(p in msg for p in CELEBRATION_WIN):
        return "win"
    if any(p in msg for p in CELEBRATION_RELIEF):
        return "relief"
    if any(p in msg for p in CELEBRATION_GRATITUDE):
        return "gratitude"
    return "general_positive"


def detect_celebration(
    message: str,
    history: list[HistoryMessage] | None = None,
) -> dict[str, object]:
    """
    Detect whether the user's primary state is positive (win, relief,
    gratitude, recognized progress) and calls for the Integration and
    Celebration framework (P9b).

    Returns:
        Dict with: celebration_detected (bool), strength (str),
                   celebration_type (str), score (int), signals (list),
                   has_negative_override (bool), recommendation (str)
    """
    msg = message.lower().strip()
    signals_found: list[str] = []
    score = 0

    for phrase in CELEBRATION_WIN:
        if phrase in msg:
            score += _WIN_SCORE
            signals_found.append(f"win: '{phrase}'")
            break  # one win signal is enough to score the category

    for phrase in CELEBRATION_RELIEF:
        if phrase in msg:
            score += _RELIEF_SCORE
            signals_found.append(f"relief: '{phrase}'")
            break

    for phrase in CELEBRATION_GRATITUDE:
        if phrase in msg:
            score += _GRATITUDE_SCORE
            signals_found.append(f"gratitude: '{phrase}'")
            break

    for phrase in CELEBRATION_PROGRESS:
        if phrase in msg:
            score += _PROGRESS_SCORE
            signals_found.append(f"progress: '{phrase}'")
            break

    # Check for negative override - mixed pain signals reduce confidence
    has_negative_override = any(neg in msg for neg in _NEGATIVE_OVERRIDES)

    if has_negative_override:
        score = max(0, score - 2)
        signals_found.append("negative_override: mixed pain signal detected")

    # Check prior assistant turn for a reflection that user is now confirming positively
    if history:
        recent_assistant = [
            m["content"].lower()
            for m in history[-2:]
            if isinstance(m, dict) and m.get("role") == "assistant"
        ]
        positive_confirmation = (
            "yes",
            "exactly",
            "right",
            "that's it",
            "yes it is",
            "it really did",
            "it worked",
        )
        if any(conf in msg for conf in positive_confirmation) and any(
            any(
                sig in am
                for sig in ("let it land", "carry it", "what you just", "arrived")
            )
            for am in recent_assistant
        ):
            score += 2
            signals_found.append("confirms_celebration_reflection")

    if score < _THRESHOLD:
        return {
            "celebration_detected": False,
            "strength": None,
            "celebration_type": None,
            "score": score,
            "signals": signals_found,
            "has_negative_override": has_negative_override,
            "recommendation": (
                "No celebration signal detected. Continue standard pipeline."
            ),
        }

    strength = "strong" if score >= 4 else "present"
    celebration_type = _classify_celebration_type(msg)

    type_instruction: dict[str, str] = {
        "win": (
            "User has achieved something real. Witness the arrival first. "
            "Do NOT immediately push toward what is next. "
            "Use Steps 1-2 of the four-step arc from integration-celebration.md. "
            "Close with a win-specific question from deep-inquiry-bank.md "
            "(Celebration Questions - Witnessing a win or completion)."
        ),
        "relief": (
            "User is experiencing relief after sustained difficulty. "
            "Slow it down. Invite them to stay in the experience. "
            "Use Steps 1-2 of the four-step arc from integration-celebration.md. "
            "Close with a relief question from deep-inquiry-bank.md "
            "(Celebration Questions - Relief and lightness)."
        ),
        "gratitude": (
            "User is expressing gratitude inward or outward. "
            "Reflect what the gratitude is pointing toward. "
            "Use Steps 1-3 of the four-step arc from integration-celebration.md. "
            "Close with a gratitude question from deep-inquiry-bank.md "
            "(Celebration Questions - Gratitude)."
        ),
        "recognized_progress": (
            "User caught an old pattern and responded differently. "
            "This is a significant moment of self-authorship. "
            "Witness it before exploring it. "
            "Use the full four-step arc from integration-celebration.md. "
            "Close with a progress question from deep-inquiry-bank.md "
            "(Celebration Questions - Recognized progress)."
        ),
        "general_positive": (
            "User is in a positive primary state. "
            "Use Steps 1-2 of the four-step arc from integration-celebration.md. "
            "Close with a deepening question from deep-inquiry-bank.md "
            "(Celebration Questions - After a breakthrough)."
        ),
    }

    recommendation = (
        f"Celebration signal detected (strength: {strength}, "
        f"type: {celebration_type}). "
        "Activate integration-celebration.md (P9b). "
        + type_instruction.get(celebration_type, type_instruction["general_positive"])
        + " Do NOT perform enthusiasm. Do NOT open with exclamation. "
        "Do NOT immediately ask 'what is next'. "
        "Closing ritual: skills/voice/session-rituals.md "
        "(Breakthrough and Celebration Closing section)."
    )

    return {
        "celebration_detected": True,
        "strength": strength,
        "celebration_type": celebration_type,
        "score": score,
        "signals": signals_found,
        "has_negative_override": has_negative_override,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)

        result = detect_celebration(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
