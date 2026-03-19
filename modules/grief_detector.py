"""Detect grief signals that should override standard reflection."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_list_field, require_str_field

HistoryMessage = dict[str, str]

ACUTE_GRIEF = [
    "they died",
    "he died",
    "she died",
    "passed away",
    "just lost",
    "just found out",
    "died yesterday",
    "died last week",
    "died this morning",
    "funeral",
    "grief",
    "grieving",
    "mourning",
    "bereavement",
    "can't believe they're gone",
    "they're gone",
    "she's gone",
    "he's gone",
    "miss them so much",
    "miss her so much",
    "miss him so much",
    "losing my mind without",
    "nothing without them",
    "the worst pain i've ever",
    "don't know how to do this",
    "doesn't feel real",
    "can't accept it",
]

ANTICIPATORY_GRIEF = [
    "watching them decline",
    "every day feels like goodbye",
    "already mourning them",
    "losing them before they're gone",
    "terminal diagnosis",
    "they don't have long",
    "running out of time",
    "saying goodbye slowly",
    "caregiving",
    "hospice",
    "watching them disappear",
    "not the same person anymore",
]

AMBIGUOUS_LOSS = [
    "no one understands why i'm upset",
    "not allowed to be this sad",
    "it's not like they died",
    "no one sees this as a real loss",
    "disenfranchised grief",
    "end of a friendship",
    "lost a friend",
    "estrangement",
    "estranged",
    "miscarriage",
    "pregnancy loss",
    "lost my sense of self",
    "lost who i was",
    "don't know if i'm allowed to grieve",
]

COMPLICATED_GRIEF = [
    "feel guilty that i feel relieved",
    "relieved they're gone",
    "loved them and they hurt me",
    "grieving someone who hurt me",
    "complicated feelings about their death",
    "don't know how to grieve",
    "angry at them for dying",
    "angry that they left",
    "toxic relationship",
    "abusive",
    "mixed feelings about losing them",
    "love and hate at the same time",
]


def detect_grief(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    msg = message.lower().strip()
    signals = []
    score = 0
    grief_type = None

    for phrase in ACUTE_GRIEF:
        if phrase in msg:
            score += 3
            signals.append(f"acute: '{phrase}'")
            grief_type = "acute"
            break

    for phrase in ANTICIPATORY_GRIEF:
        if phrase in msg:
            score += 2
            signals.append(f"anticipatory: '{phrase}'")
            if not grief_type:
                grief_type = "anticipatory"
            break

    for phrase in AMBIGUOUS_LOSS:
        if phrase in msg:
            score += 2
            signals.append(f"ambiguous: '{phrase}'")
            if not grief_type:
                grief_type = "ambiguous"
            break

    for phrase in COMPLICATED_GRIEF:
        if phrase in msg:
            score += 2
            signals.append(f"complicated: '{phrase}'")
            if not grief_type:
                grief_type = "complicated"
            break

    if history:
        recent = [
            m["content"].lower()
            for m in history
            if isinstance(m, dict) and m.get("role") == "user"
        ][-4:]
        all_grief = ACUTE_GRIEF[:8] + ANTICIPATORY_GRIEF[:4] + AMBIGUOUS_LOSS[:4]
        if sum(1 for m in recent if any(p in m for p in all_grief)) >= 2:
            score += 2
            signals.append("sustained_grief_across_messages")

    if score < 2:
        return {
            "grief_detected": False,
            "grief_type": None,
            "score": score,
            "signals": [],
        }

    type_guidance = {
        "acute": "Sanctuary only. No questions for first 2-3 exchanges. Witness the loss. Use grief language from skills/frameworks/grief-companion.md.",
        "anticipatory": "Gentle witness. Follow the user's lead. One question when appropriate. No silver linings about what comes after.",
        "ambiguous": "VALIDATE first: 'Just because others don't see it as a loss doesn't mean it isn't one.' Then witness.",
        "complicated": "Hold both feelings at once. Do not try to resolve complexity. 'It's possible to grieve someone and be angry at them at the same time.'",
    }

    return {
        "grief_detected": True,
        "grief_type": grief_type or "acute",
        "score": score,
        "signals": signals,
        "recommendation": (
            f"Activate grief_companion.md. Type: {grief_type}. "
            f"{type_guidance.get(grief_type or '', '')} "
            "Retrieve grief questions from deep-inquiry-bank.md — 'Grief Questions' section."
        ),
    }


if __name__ == "__main__":
    try:
        data = parse_json_object(sys.stdin.read().strip())
        result = detect_grief(
            require_str_field(data, "message"),
            require_list_field(data, "history"),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
