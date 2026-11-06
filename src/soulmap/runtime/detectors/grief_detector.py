"""Detect grief signals that should override standard reflection."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from soulmap.runtime.knowledge.keyword_lists import (
    load_keyword_section,
    load_labeled_groups,
    load_runtime_guidance,
)
from soulmap.runtime.knowledge.runtime_config import DETECTOR_CONFIG
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/grief-companion.md,
# "## Detection signals". Nothing is hardcoded here.
_GRIEF_GROUPS = load_labeled_groups(
    runtime_skill_path("grief-companion"), "Detection signals"
)
_RULES = DETECTOR_CONFIG["grief"]
_SKILL_PATH = runtime_skill_path("grief-companion")
_READINESS_SIGNALS = load_keyword_section(_SKILL_PATH, "Readiness signals")
_GUIDANCE = load_runtime_guidance(_SKILL_PATH)
ACUTE_GRIEF = _GRIEF_GROUPS["acute grief"]
ANTICIPATORY_GRIEF = _GRIEF_GROUPS["anticipatory grief"]
AMBIGUOUS_LOSS = _GRIEF_GROUPS["ambiguous loss"]
COMPLICATED_GRIEF = _GRIEF_GROUPS["complicated grief"]

HistoryMessage = dict[str, str]


def detect_grief(
    message: str, history: list[HistoryMessage] | None = None
) -> dict[str, object]:
    """Score grief signals in the current message.

    Matches the phrase groups authored in
    ``skills/frameworks/grief-companion.md``: acute grief, anticipatory grief,
    ambiguous loss, and complicated grief. Acute grief is checked first, since
    it routes to the shortest and most held response.

    Args:
        message: The user's current message.
        history: Prior turns, used to measure sustained grief and the number of
            user exchanges since the first acute-grief signal.

    Returns:
        A dict with ``grief_detected``, ``grief_type``, ``score``,
        ``signals``, and ``recommendation``.
    """
    msg = message.lower().strip()
    signals = []
    score = 0
    grief_type = None

    for phrase in ACUTE_GRIEF:
        if phrase in msg:
            score += int(_RULES["Acute grief weight"])
            signals.append(f"acute: '{phrase}'")
            grief_type = "acute"
            break

    for phrase in ANTICIPATORY_GRIEF:
        if phrase in msg:
            score += int(_RULES["Anticipatory grief weight"])
            signals.append(f"anticipatory: '{phrase}'")
            if not grief_type:
                grief_type = "anticipatory"
            break

    for phrase in AMBIGUOUS_LOSS:
        if phrase in msg:
            score += int(_RULES["Ambiguous loss weight"])
            signals.append(f"ambiguous: '{phrase}'")
            if not grief_type:
                grief_type = "ambiguous"
            break

    for phrase in COMPLICATED_GRIEF:
        if phrase in msg:
            score += int(_RULES["Complicated grief weight"])
            signals.append(f"complicated: '{phrase}'")
            if not grief_type:
                grief_type = "complicated"
            break

    user_history = [
        item["content"].lower()
        for item in (history or [])
        if isinstance(item, dict) and item.get("role") == "user"
    ]
    recent = user_history[-int(_RULES["Recent user history window"]) :]
    history_grief_signals = (
        ACUTE_GRIEF + ANTICIPATORY_GRIEF + AMBIGUOUS_LOSS + COMPLICATED_GRIEF
    )
    def acute_loss_anchor(text: str) -> str | None:
        """Return the most specific Markdown-authored explicit loss anchor."""
        anchors = [
            phrase
            for phrase in ACUTE_GRIEF
            if phrase in text
            and "my " in phrase
            and any(marker in phrase for marker in ("died", "passed away", "lost"))
        ]
        return max(anchors, key=len) if anchors else None

    current_loss_anchor = acute_loss_anchor(msg)
    current_grief_sequence: list[str] = []
    active_loss_anchor: str | None = None
    for prior in reversed(user_history):
        if not any(phrase in prior for phrase in history_grief_signals):
            break
        prior_loss_anchor = acute_loss_anchor(prior)
        if prior_loss_anchor:
            if active_loss_anchor is None:
                active_loss_anchor = prior_loss_anchor
            elif prior_loss_anchor != active_loss_anchor:
                break
        current_grief_sequence.append(prior)
    current_grief_sequence.reverse()
    if (
        current_loss_anchor
        and active_loss_anchor
        and current_loss_anchor != active_loss_anchor
    ):
        # A newly named loss starts its own acute-grief exchange window.
        current_grief_sequence = []
    first_acute = next(
        (
            index
            for index, prior in enumerate(current_grief_sequence)
            if any(phrase in prior for phrase in ACUTE_GRIEF)
        ),
        None,
    )
    readiness_detected = any(phrase in msg for phrase in _READINESS_SIGNALS)
    current_turn_continues_grief = readiness_detected or any(
        phrase in msg for phrase in history_grief_signals
    )
    acute_exchange_count = (
        len(current_grief_sequence) - first_acute + int(current_turn_continues_grief)
        if first_acute is not None
        else int(any(phrase in msg for phrase in ACUTE_GRIEF))
    )

    if history:
        all_grief = (
            ACUTE_GRIEF[: int(_RULES["Acute history signal limit"])]
            + ANTICIPATORY_GRIEF[: int(_RULES["Anticipatory history signal limit"])]
            + AMBIGUOUS_LOSS[: int(_RULES["Ambiguous history signal limit"])]
        )
        if sum(1 for m in recent if any(p in m for p in all_grief)) >= int(
            _RULES["Sustained history threshold"]
        ):
            score += int(_RULES["Sustained grief weight"])
            signals.append("sustained_grief_across_messages")

    if score < int(_RULES["Minimum detection score"]):
        return {
            "grief_detected": False,
            "grief_type": None,
            "score": score,
            "signals": [],
            "acute_exchange_count": acute_exchange_count,
            "readiness_detected": readiness_detected,
        }

    detected_type = grief_type or "acute"
    recommendation = (
        f"{_GUIDANCE['detected_prefix']} {detected_type}. "
        f"{_GUIDANCE.get(detected_type, '')} {_GUIDANCE['detected_suffix']}"
    )

    return {
        "grief_detected": True,
        "grief_type": detected_type,
        "score": score,
        "signals": signals,
        "acute_exchange_count": acute_exchange_count,
        "readiness_detected": readiness_detected,
        "recommendation": recommendation,
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
