"""Detect existential territory that needs holding rather than solving."""

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
    load_key_value_table,
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/existential-companion.md,
# "## Detection signals". Nothing is hardcoded here.
_EXISTENTIAL_GROUPS = load_labeled_groups(
    default_skill_path("skills/frameworks/existential-companion.md"),
    "Detection signals",
)
IDENTITY_SHIFT = _EXISTENTIAL_GROUPS["identity shift"]
LARGER_QUESTIONS = _EXISTENTIAL_GROUPS["larger philosophical questions"]
ENDINGS_GRIEF = _EXISTENTIAL_GROUPS["endings and transitions"]
MEANING_DEPTH = _EXISTENTIAL_GROUPS["depth of meaning"]
HOLDING_QUESTIONS = _EXISTENTIAL_GROUPS["holding a question"]
_EXISTENTIAL_SCORING = load_key_value_table(
    default_skill_path("skills/frameworks/existential-companion.md"), "Scoring"
)
_EXISTENTIAL_GUIDANCE = load_key_value_table(
    default_skill_path("skills/frameworks/existential-companion.md"), "Guidance"
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
    """Detect existential territory in the user's message.

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

    signal_sources = {
        "identity_shift": IDENTITY_SHIFT,
        "meaning_depth": MEANING_DEPTH,
        "endings_grief": ENDINGS_GRIEF,
        "larger_questions": LARGER_QUESTIONS,
        "holding": HOLDING_QUESTIONS,
    }
    signal_weights = {
        "identity_shift": int(_EXISTENTIAL_SCORING["Identity-shift weight"]),
        "meaning_depth": int(_EXISTENTIAL_SCORING["Meaning-depth weight"]),
        "endings_grief": int(_EXISTENTIAL_SCORING["Endings-grief weight"]),
        "larger_questions": int(_EXISTENTIAL_SCORING["Larger-questions weight"]),
        "holding": int(_EXISTENTIAL_SCORING["Holding-question weight"]),
    }
    signal_map = [
        (name, signal_sources[name], signal_weights[name])
        for name in _EXISTENTIAL_SCORING["Territory priority"].split(";")
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
        ][-int(_EXISTENTIAL_SCORING["Recent user history window"]) :]
        returning_signals = (
            IDENTITY_SHIFT[
                : int(_EXISTENTIAL_SCORING["Sustained identity signal limit"])
            ]
            + MEANING_DEPTH[
                : int(_EXISTENTIAL_SCORING["Sustained meaning signal limit"])
            ]
            + ENDINGS_GRIEF[
                : int(_EXISTENTIAL_SCORING["Sustained endings signal limit"])
            ]
            + LARGER_QUESTIONS[
                : int(_EXISTENTIAL_SCORING["Sustained larger-question signal limit"])
            ]
        )
        count = sum(
            1
            for past in recent_user
            if any(phrase in past for phrase in returning_signals)
        )
        if count >= int(_EXISTENTIAL_SCORING["Sustained history threshold"]):
            score += int(_EXISTENTIAL_SCORING["Sustained-territory bonus"])
            signals_found.append(
                "sustained: existential territory across multiple messages"
            )

    if score < int(_EXISTENTIAL_SCORING["Minimum detection score"]):
        return {
            "existential_detected": False,
            "territory": None,
            "score": score,
            "signals": signals_found,
            "recommendation": "No existential signals detected. Continue standard pipeline.",
        }

    territory = _classify_territory(msg, territory_scores)

    territory_guidance = _EXISTENTIAL_GUIDANCE

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
