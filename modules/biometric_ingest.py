"""Ingests biometric data (Oura/Apple Health) and maps them to somatic markers safely."""

from __future__ import annotations

import json
import sys

from modules.cli_payload import parse_json_object, require_dict_field


def map_biometrics_to_somatic_prompt(
    biometrics: dict[str, object],
) -> dict[str, object]:
    """Translates wearable numbers to a neutral, mirror-ready somatic reflection."""

    # Safe checks
    hrv = biometrics.get("hrv")
    sleep = biometrics.get("sleep_score")

    signals = []
    if isinstance(hrv, int | float) and hrv < 30:
        signals.append("Heart rate variability suggests high physiological load.")

    if isinstance(sleep, int | float) and sleep < 50:
        signals.append("Sleep architecture indicates insufficient rest/recovery.")

    if not signals:
        return {"status": "NO_SOMATIC_ALERT", "context": None}

    summary = " ".join(signals)
    return {
        "status": "BIOMETRIC_ALERT",
        "context": summary,
        "instruction": (
            "Acknowledge emotional state first. Then use biometric data as a reflective indicator "
            "— NOT diagnostic. Use somatic_wellbeing.md. "
            "Follow with ONE question: 'What does this reflect in your inner experience right now?'"
        ),
    }


def main() -> int:
    data = parse_json_object(sys.stdin.read())
    biometrics = require_dict_field(data, "biometrics")

    result = map_biometrics_to_somatic_prompt(biometrics)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
