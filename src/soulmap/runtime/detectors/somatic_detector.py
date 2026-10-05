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
    load_key_value_table,
    load_labeled_groups,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/somatic-wellbeing.md,
# "## Detection signals". Nothing is hardcoded here.
_SOMATIC_GROUPS = load_labeled_groups(
    runtime_skill_path("somatic-wellbeing"), "Detection signals"
)
_RULES = load_key_value_table(
    runtime_skill_path("somatic-wellbeing"),
    "Runtime detection contract",
)
_GUIDANCE = load_key_value_table(runtime_skill_path("somatic-wellbeing"), "Guidance")
BODY_SENSATION = _SOMATIC_GROUPS["body sensation language"]
SOMATIC_INVITATION = _SOMATIC_GROUPS["somatic invitation"]
BIOMETRIC = _SOMATIC_GROUPS["biometric context"]
_SOMATIC_TYPES = load_key_value_table(
    runtime_skill_path("somatic-wellbeing"), "Detection type mapping"
)


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
            score += int(_RULES["Biometric context weight"])
            signals.append(f"biometric:'{p}'")
            mode = _SOMATIC_TYPES["biometric context"]
            break

    for p in BODY_SENSATION:
        if p in msg:
            score += int(_RULES["Body sensation weight"])
            signals.append(f"body:'{p}'")
            if not mode:
                mode = _SOMATIC_TYPES["body sensation language"]
            break

    for p in SOMATIC_INVITATION:
        if p in msg:
            score += int(_RULES["Somatic invitation weight"])
            signals.append(f"invitation:'{p}'")
            if not mode:
                mode = _SOMATIC_TYPES["somatic invitation"]
            break

    if score < int(_RULES["Minimum detection score"]):
        return {"somatic_detected": False, "mode": None}

    guidance = _GUIDANCE.get(mode or "", "")

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
