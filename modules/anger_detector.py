"""Detect anger signals that can activate the anger companion layer."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]

ACTIVE_ANGER = [
    "i'm so angry",
    "i am so angry",
    "i'm furious",
    "i'm livid",
    "i'm so frustrated",
    "makes me furious",
    "makes me so angry",
    "i could scream",
    "i want to scream",
    "i want to explode",
    "i'm fed up",
    "i'm sick of this",
    "i'm sick of them",
    "i'm enraged",
    "i'm seething",
    "boiling inside",
    "how dare they",
    "how dare he",
    "how dare she",
    "this is so unfair",
    "it's not fair",
    "this isn't right",
    "i hate this",
    "i hate them",
    "i hate him",
    "i hate her",
    "i'm so done",
    "i can't stand it",
    "i can't take it anymore",
    "i'm disgusted",
    "i'm outraged",
]

SELF_ANGER = [
    "i'm so angry at myself",
    "i'm furious at myself",
    "i hate myself",
    "i'm disgusted with myself",
    "i can't believe i did that",
    "how could i be so stupid",
    "i'm so disappointed in myself",
]

RESIDUAL_ANGER = [
    "still so angry about",
    "can't let go of the anger",
    "the anger won't go away",
    "i keep getting angry about",
    "every time i think about it i get angry",
    "i've been angry for",
    "been holding this anger",
    "the resentment",
    "bitter about",
    "i resent",
]


def detect_anger(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    msg = message.lower().strip()
    signals = []
    score = 0
    anger_type = None

    for phrase in ACTIVE_ANGER:
        if phrase in msg:
            score += 3
            signals.append(f"active: '{phrase}'")
            anger_type = "active"
            break

    for phrase in SELF_ANGER:
        if phrase in msg:
            score += 3
            signals.append(f"self_anger: '{phrase}'")
            if not anger_type:
                anger_type = "self_anger"
            break

    for phrase in RESIDUAL_ANGER:
        if phrase in msg:
            score += 2
            signals.append(f"residual: '{phrase}'")
            if not anger_type:
                anger_type = "residual"
            break

    if history and anger_type == "active":
        recent = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-3:]
        anger_count = sum(1 for m in recent if any(p in m for p in ACTIVE_ANGER[:8]))
        if anger_count >= 2:
            score += 2
            signals.append("sustained_anger_across_messages")

    if score < 2:
        return {
            "anger_detected": False,
            "anger_type": None,
            "score": score,
            "signals": [],
        }

    guidance_map = {
        "active": (
            "Active anger present. Phase 1 first: meet the anger before exploring it. "
            "'The anger makes complete sense. Something was crossed here  -  something that matters.' "
            "Do NOT jump to 'what's underneath' yet. Then Phase 2: name what it's protecting. "
            "Phase 3: surface the need under the demand. "
            "See skills/frameworks/anger-companion.md for full protocol."
        ),
        "self_anger": (
            "Anger turned inward. Activate skills/frameworks/self-compassion.md as primary. "
            "Anger at self is often grief, fear, or perfectionism using anger's force. "
            "Initial frame: 'The anger is turned inward right now. What was it trying to protect you from?'"
        ),
        "residual": (
            "Residual/chronic anger. The anger has been held for some time. "
            "Acknowledge the weight of carrying it: 'That's a long time to carry something this heavy.' "
            "Then explore what the anger is still protecting  -  what hasn't been resolved."
        ),
    }

    return {
        "anger_detected": True,
        "anger_type": anger_type,
        "score": score,
        "signals": signals,
        "note": "Anger companion  -  meet the anger before exploring it.",
        "recommendation": guidance_map.get(anger_type or "", ""),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        result = detect_anger(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
