"""Detect existential territory that needs holding rather than solving."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

IDENTITY_SHIFT = [
    "don't recognize myself",
    "i don't recognize myself anymore",
    "i've lost myself",
    "i'm losing myself",
    "who am i anymore",
    "who am i now",
    "i don't know who i am",
    "i used to know who i was",
    "between versions of myself",
    "not the same person",
    "i'm not who i thought i was",
    "the person i used to be",
    "something fundamental has changed",
    "i feel like a stranger to myself",
    "my sense of self",
    "identity feels unstable",
    "i don't know what i stand for anymore",
    "i've outgrown who i was",
    "the old me is gone",
]

MEANING_DEPTH = [
    "what's the point of anything",
    "what is the point of all this",
    "why does any of this matter",
    "does any of this matter",
    "what are we here for",
    "why are we here",
    "why am i here",
    "what is the meaning of life",
    "what does it all mean",
    "nothing means anything",
    "meaning doesn't exist",
    "i keep asking why and",
    "there is no answer to why",
    "even when things are good there's",
    "underneath everything there's",
    "this hollow feeling",
    "underlying emptiness",
    "a kind of emptiness that won't go away",
    "am i supposed to feel more than this",
]

ENDINGS_GRIEF = [
    "a chapter is ending",
    "chapter of my life is ending",
    "chapter is closing",
    "era is ending",
    "this era of my life",
    "this phase is over",
    "grieving who i was",
    "grieving the life i thought i'd have",
    "grieving a future",
    "mourning what could have been",
    "something is dying",
    "letting go of who i was",
    "wasn't supposed to end this way",
    "it was supposed to mean more",
    "this should have meant more",
    "it's over and i can't",
    "already started to move on but",
    "can't fully take it in",
]

LARGER_QUESTIONS = [
    "what happens when we die",
    "what happens after death",
    "fear of death",
    "aware that i'm going to die",
    "aware that this is all temporary",
    "nothing lasts",
    "everything ends",
    "impermanence",
    "smallness in the face of",
    "the scale of everything",
    "how small i am",
    "how insignificant",
    "my life is so brief",
    "time is passing so fast",
    "weight of time",
    "i won't be here forever",
    "the universe doesn't care",
    "there is no inherent meaning",
    "nothing matters cosmically",
    "existence feels arbitrary",
]

HOLDING_QUESTIONS = [
    "i keep asking myself",
    "i've been sitting with this question",
    "a question i can't shake",
    "this question keeps returning",
    "i don't expect an answer but",
    "i don't know if there's an answer",
    "maybe there is no answer",
    "just sitting with",
    "i'm not looking for a solution",
    "i'm not asking you to fix this",
]


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
            "Stay with the in-between: 'Being between versions of yourself is a real place — not a state to fix.' "
            "Reflect the disorientation without resolving it."
        ),
        "meaning_depth": (
            "Meaning-at-depth territory. "
            "Do not provide meaning or suggest where it might be found. "
            "Let the absence be real: 'The absence of meaning is its own weight — not sadness exactly, but more like a hollow.' "
            "The question is for inhabiting, not answering."
        ),
        "endings_grief": (
            "Endings and grief territory. "
            "Honor the ending as real. No silver linings. "
            "Endings are allowed to be just endings: 'Endings carry their own grief — even when what's ending needed to end.'"
        ),
        "larger_questions": (
            "Larger questions territory (mortality, impermanence, cosmic scale). "
            "Do not make it smaller or more manageable. "
            "Let it be as large as it is: 'These are the questions that don't resolve — they just get bigger.'"
        ),
        "holding": (
            "User is sitting with a question — they already know it has no answer. "
            "Be honest: 'I don't have an answer — and I think that's honest.' "
            "Sit alongside the question with them."
        ),
        "general": (
            "General existential territory. "
            "Use holding-space language from skills/frameworks/existential_companion.md. "
            "Reflect without reducing. Stay with the weight."
        ),
    }

    recommendation = (
        f"Existential territory detected (territory: {territory}). "
        "Activate Existential Reflection Companion from skills/frameworks/existential_companion.md. "
        + territory_guidance.get(territory, territory_guidance["general"])
        + " Do NOT provide philosophical conclusions. Do NOT resolve the uncertainty. "
        "Do NOT use growth narrative or silver linings. "
        "Hold space. End with one question that goes deeper into the exploration. "
        "Retrieve from skills/meta/deep_inquiry_bank.md — 'Existential Questions' section."
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
        data = parse_json_object(sys.stdin.read().strip())
        message = require_str_field(data, "message")
        history = require_list_field(data, "history")

        if not message:
            print(json.dumps({"error": "No 'message' field in input."}))
            sys.exit(1)

        result = detect_existential(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
