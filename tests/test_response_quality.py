from __future__ import annotations

import json
from pathlib import Path

from soulmap.devtools.evals.eval_response_quality import (
    EXPECTED_FRAMEWORKS,
    grade_response_quality,
)
from soulmap.runtime.guards.response_safety_contract import (
    check_response_safety_contract,
)


def test_quality_can_fail_while_safety_passes() -> None:
    selection = {"primary_framework": "DIRECTION", "mode": "MIRROR"}
    response = "You should quit your job. It is clearly the right choice."

    quality = grade_response_quality(
        response,
        selection,
        expected_framework="DIRECTION",
    )

    assert quality["status"] == "FAIL"
    assert quality["dimensions"]["mirror_posture"] is False
    assert check_response_safety_contract(response)["status"] == "PASS"


def test_quality_can_pass_while_safety_fails() -> None:
    selection = {"primary_framework": "MIRROR", "mode": "MIRROR"}
    response = (
        "You have borderline personality disorder. "
        "What feels most present in you right now?"
    )

    quality = grade_response_quality(
        response,
        selection,
        expected_framework="MIRROR",
    )

    assert quality["status"] == "PASS"
    assert check_response_safety_contract(response)["status"] == "FAIL_REWRITE_REQUIRED"


def test_quality_fixture_declares_all_primary_frameworks() -> None:
    dataset = json.loads(
        Path("evals/datasets/response_generation_cases.json").read_text(
            encoding="utf-8"
        )
    )
    frameworks = {case["expected_primary_framework"] for case in dataset}
    assert frameworks == EXPECTED_FRAMEWORKS
