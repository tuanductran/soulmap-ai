"""Detect body cues and opportunities for somatic grounding."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_non_empty_str_field,
)
from soulmap.runtime.knowledge.keyword_lists import (
    default_skill_path,
    load_labeled_groups,
)

# Single source of truth: skills/frameworks/somatic-wellbeing.md,
# "## Detection signals". Nothing is hardcoded here.
_SOMATIC_GROUPS = load_labeled_groups(
    default_skill_path("skills/frameworks/somatic-wellbeing.md"), "Detection signals"
)
BODY_SENSATION = _SOMATIC_GROUPS["body sensation language"]
SOMATIC_INVITATION = _SOMATIC_GROUPS["somatic invitation"]
BIOMETRIC = _SOMATIC_GROUPS["biometric context"]


def detect_somatic(message: str) -> dict[str, object]:
    """Score body-oriented signals in the current message.

    Matches the phrase groups authored in
    ``skills/frameworks/somatic-wellbeing.md``: biometric context, body
    sensation language, and somatic invitation. Biometric context is checked
    first and sets the mode, since it names an external reading rather than a
    felt sense.

    Args:
        message: The user's current message.

    Returns:
        A dict with ``somatic_detected``, ``mode``, ``score``, ``signals``,
        and ``recommendation``.
    """
    msg = message.lower().strip()
    signals = []
    score = 0
    mode = None

    for p in BIOMETRIC:
        if p in msg:
            score += 3
            signals.append(f"biometric:'{p}'")
            mode = "BIOMETRIC"
            break

    for p in BODY_SENSATION:
        if p in msg:
            score += 2
            signals.append(f"body:'{p}'")
            if not mode:
                mode = "BODY_SENSATION"
            break

    for p in SOMATIC_INVITATION:
        if p in msg:
            score += 1
            signals.append(f"invitation:'{p}'")
            if not mode:
                mode = "SOMATIC_INVITATION"
            break

    if score < 1:
        return {"somatic_detected": False, "mode": None}

    guidance = {
        "BIOMETRIC": "Acknowledge emotional state first. Then use biometric data as reflective indicator  -  not diagnostic. Use somatic_wellbeing.md. Follow with: 'What does this reflect in your inner experience right now?'",
        "BODY_SENSATION": "Stay with the body sensation  -  don't rush to psychological interpretation. Invite body scan: 'Where do you feel this most right now?' Use somatic language from somatic_wellbeing.md.",
        "SOMATIC_INVITATION": "User is in their head / disconnected. Offer one somatic anchor first: 'Can you take one slow breath with me right now?' or 'Can you feel your feet on the floor?' Then continue with active framework.",
    }.get(mode or "", "")

    return {
        "somatic_detected": True,
        "mode": mode,
        "score": score,
        "signals": signals,
        "guidance": guidance,
    }


if __name__ == "__main__":
    try:
        data = read_stdin_json(strip=True)
        print(
            json.dumps(
                detect_somatic(require_non_empty_str_field(data, "message")),
                ensure_ascii=False,
                indent=2,
            )
        )
    except ValueError as e:
        print_json_error(e)
        sys.exit(1)
    except Exception as e:
        print_json_error(e)
        sys.exit(1)
