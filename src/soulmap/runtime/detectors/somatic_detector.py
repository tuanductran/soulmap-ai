"""Detect body cues and opportunities for somatic grounding."""

from __future__ import annotations

import json
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_non_empty_str_field,
)
from soulmap.runtime.io.text_normalization import mask_third_party_attribution
from soulmap.runtime.knowledge.keyword_lists import (
    load_labeled_groups,
    load_runtime_guidance,
)
from soulmap.runtime.knowledge.runtime_config import DETECTOR_CONFIG
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

# Single source of truth: skills/frameworks/somatic-wellbeing.md,
# "## Detection signals". Nothing is hardcoded here.
_SOMATIC_GROUPS = load_labeled_groups(
    runtime_skill_path("somatic-wellbeing"), "Detection signals"
)
_RULES = DETECTOR_CONFIG["somatic"]
_GUIDANCE = load_runtime_guidance(runtime_skill_path("somatic-wellbeing"))
BODY_SENSATION = _SOMATIC_GROUPS["body sensation language"]
SOMATIC_INVITATION = _SOMATIC_GROUPS["somatic invitation"]
BIOMETRIC = _SOMATIC_GROUPS["biometric context"]


def detect_somatic(message: str) -> dict[str, object]:
    """Recognize somatic activation cues separately from context-only signals.

    Biometric readings and general cognitive/disconnection phrases are useful
    context, but they do not activate the Somatic secondary layer. Activation
    requires user-described body sensation language or an explicit request for
    body-awareness or grounding support.

    Args:
        message: The user's current message.

    Returns:
        Detection state, context flags, matched signals, score, and guidance.
    """
    msg = mask_third_party_attribution(message)
    signals = []
    score = 0
    biometric_detected = False
    body_detected = False
    invitation_detected = False
    mode = None

    for p in BIOMETRIC:
        if p in msg:
            score += int(_RULES["Biometric context weight"])
            signals.append(f"biometric:'{p}'")
            biometric_detected = True
            break

    for p in BODY_SENSATION:
        if p in msg:
            score += int(_RULES["Body sensation weight"])
            signals.append(f"body:'{p}'")
            body_detected = True
            mode = "BODY_SENSATION"
            break

    for p in SOMATIC_INVITATION:
        if p in msg:
            score += int(_RULES["Somatic invitation weight"])
            signals.append(f"invitation:'{p}'")
            invitation_detected = True
            if not body_detected:
                mode = "SOMATIC_INVITATION"
            break

    if score < int(_RULES["Minimum detection score"]):
        return {
            "somatic_detected": False,
            "biometric_context_detected": False,
            "mode": None,
        }

    if mode is None and biometric_detected:
        mode = "BIOMETRIC"

    guidance = _GUIDANCE.get(mode or "", "")

    return {
        "somatic_detected": body_detected or invitation_detected,
        "biometric_context_detected": biometric_detected,
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
