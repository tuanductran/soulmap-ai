"""Detect grief signals that should override standard reflection."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.config import (
    ACUTE_GRIEF,
    AMBIGUOUS_LOSS,
    ANTICIPATORY_GRIEF,
    COMPLICATED_GRIEF,
)
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)

HistoryMessage = dict[str, str]


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
            "Retrieve grief questions from deep-inquiry-bank.md  -  'Grief Questions' section."
        ),
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        message, history = require_message_history_fields(data)
        result = detect_grief(message, history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
