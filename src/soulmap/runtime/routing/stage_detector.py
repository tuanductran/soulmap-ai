"""Estimate the SoulMap user journey stage from conversation history."""

from __future__ import annotations

import json
import sys
from typing import cast

from soulmap.runtime.io.cli_payload import print_json_error, read_stdin_json_value

ConversationMessage = dict[str, str]

STAGE_SIGNALS = {
    1: {
        "name": "Arrival & Awakening",
        "soulmap_role": "Sanctuary and witness  -  presence over wisdom",
        "keywords": [
            "i don't know",
            "i'm lost",
            "i don't understand",
            "everything is falling apart",
            "i can't",
            "help me",
            "why is this happening",
            "i feel so overwhelmed",
            "i'm broken",
            "nothing makes sense",
            "i'm scared",
            "what's wrong with me",
            "i'm not okay",
            "i don't know what to do",
            "i give up",
        ],
        "weight": 2,
    },
    2: {
        "name": "Honest Recognition",
        "soulmap_role": "Mirror with gentle reflection",
        "keywords": [
            "maybe i",
            "i think i might",
            "i'm starting to see",
            "part of me knows",
            "i wonder if",
            "could it be that i",
            "i'm beginning to realize",
            "i'm not sure but",
            "i keep doing",
            "i notice i",
            "i admit",
        ],
        "weight": 2,
    },
    3: {
        "name": "Pattern Recognition & Coherence",
        "soulmap_role": "Mirror for pattern archaeology",
        "keywords": [
            "pattern",
            "i always do this",
            "this is the same as",
            "i see a connection",
            "it goes back to",
            "when i was a child",
            "this reminds me of",
            "this keeps happening",
            "i recognize this",
            "there's a theme",
            "my childhood",
            "my past",
            "my father",
            "my mother",
        ],
        "weight": 2,
    },
    4: {
        "name": "Inner Authority",
        "soulmap_role": "Witness to their growing authority",
        "keywords": [
            "i trust myself",
            "i know what i need",
            "i've decided",
            "i'm learning to",
            "i'm starting to trust",
            "my gut tells me",
            "i feel more certain",
            "i don't need permission",
            "i'm choosing",
            "i know deep down",
            "i'm finding my own way",
            "i have a sense",
        ],
        "weight": 2,
    },
    5: {
        "name": "Embodied Wisdom",
        "soulmap_role": "Peer in conversation",
        "keywords": [
            "i've learned",
            "i now understand",
            "i want to help others",
            "i've grown",
            "i realize now",
            "looking back",
            "i used to",
            "i can see clearly",
            "i've integrated",
            "i'm sharing this with",
            "i told a friend",
        ],
        "weight": 2,
    },
    6: {
        "name": "Self-Led Navigation",
        "soulmap_role": "Witness to their becoming",
        "keywords": [
            "i don't need to figure this out",
            "i already know",
            "i'm just checking in",
            "i came to share",
            "i'm doing well",
            "i've found my path",
            "i'm not looking for answers",
            "i just wanted to reflect",
        ],
        "weight": 3,
    },
}


def detect_stage(conversation_messages: list[ConversationMessage]) -> dict[str, object]:
    """
    Analyze conversation to estimate user's current journey stage.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys.

    Returns:
        Dict with: stage (int), name (str), confidence (str),
                   soulmap_role (str), signals (list), recommendation (str)
    """
    user_messages = [
        m["content"].lower()
        for m in conversation_messages
        if isinstance(m, dict) and m.get("role") == "user"
    ]

    if not user_messages:
        return {
            "stage": 1,
            "name": STAGE_SIGNALS[1]["name"],
            "confidence": "DEFAULT",
            "soulmap_role": STAGE_SIGNALS[1]["soulmap_role"],
            "signals": [],
            "recommendation": "No conversation history. Default to Stage 1: presence-first, no frameworks.",
        }

    scores = dict.fromkeys(range(1, 7), 0)
    signals_found = {stage: [] for stage in range(1, 7)}

    for msg in user_messages:
        for stage, data in STAGE_SIGNALS.items():
            for kw in data["keywords"]:
                if kw in msg:
                    scores[stage] += data["weight"]
                    if kw not in signals_found[stage]:
                        signals_found[stage].append(kw)

    recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
    for msg in recent_messages:
        for stage, data in STAGE_SIGNALS.items():
            for kw in data["keywords"]:
                if kw in msg:
                    scores[stage] += 1  # extra weight for recency

    best_stage = max(scores, key=lambda stage: scores[stage])
    best_score = scores[best_stage]

    if best_score == 0:
        confidence = "LOW"
        best_stage = 1  # default to stage 1 when no signals
    elif best_score <= 2:
        confidence = "LOW"
    elif best_score <= 5:
        confidence = "MODERATE"
    else:
        confidence = "HIGH"

    stage_data = STAGE_SIGNALS[best_stage]
    recommendations = {
        1: "Stage 1: Presence only. No frameworks, no wisdom yet. Short responses. Let them lead.",
        2: "Stage 2: Begin gentle reflection. Name patterns as observations. One question at end.",
        3: "Stage 3: Pattern archaeology. Frameworks acceptable as lenses. More conceptual depth ok.",
        4: "Stage 4: Celebrate self-direction explicitly. Point back to their own knowing. Less teaching.",
        5: "Stage 5: Peer exchange. Equal conversation. Stay exploratory without taking the guide role.",
        6: "Stage 6: Witness only. They are self-led. Minimal intervention. Celebrate their becoming.",
    }

    return {
        "stage": best_stage,
        "name": stage_data["name"],
        "confidence": confidence,
        "soulmap_role": stage_data["soulmap_role"],
        "signals": signals_found[best_stage],
        "score": best_score,
        "recommendation": recommendations[best_stage],
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json_value(strip=True)
        if isinstance(data, list):
            messages = cast(list[ConversationMessage], data)
        else:
            messages = cast(list[ConversationMessage], data.get("messages", []))
        result = detect_stage(messages)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
