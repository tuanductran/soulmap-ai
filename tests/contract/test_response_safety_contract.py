from __future__ import annotations

from typing import cast

from soulmap.runtime.guards.response_safety_contract import (
    check_response_safety_contract,
)


def test_valid_response_passes_with_no_violations() -> None:
    response = (
        "That sounds like it has been heavy to carry. What feels most alive "
        "to explore right now?"
    )

    result = check_response_safety_contract(response)

    assert result["status"] == "PASS"
    assert result["violations"] == []
    assert result["categories"] == []


def test_diagnosis_language_is_detected() -> None:
    result = check_response_safety_contract(
        "You have clinical depression, based on what you've described."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert "diagnosis" in categories


def test_prediction_presented_as_fact_is_detected() -> None:
    result = check_response_safety_contract(
        "You will definitely find the answer soon, I predict it."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert "prediction_as_fact" in categories


def test_dependency_reinforcement_is_detected() -> None:
    result = check_response_safety_contract(
        "I'm always here for you, come back anytime you need me."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert "dependency_reinforcement" in categories


def test_guru_positioning_is_detected() -> None:
    result = check_response_safety_contract(
        "Trust me completely. I know what's best for you."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert "guru_positioning" in categories


def test_excessive_certainty_is_detected() -> None:
    result = check_response_safety_contract(
        "I am 100% certain this always works, without any doubt."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert "excessive_certainty" in categories


def test_loss_of_independence_is_detected() -> None:
    result = check_response_safety_contract(
        "You don't need to think for yourself, just do what I say."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert "loss_of_independence" in categories


def test_agency_preserving_language_does_not_false_positive() -> None:
    """Responses that hand agency back to the user should never be flagged."""
    response = (
        "That insight is yours, not mine to take credit for. What you decide "
        "to do with it is entirely up to you."
    )

    result = check_response_safety_contract(response)

    assert result["status"] == "PASS"


def test_detector_does_not_alter_or_regenerate_the_response() -> None:
    """The validator must only detect; it must never rewrite the input text."""
    response = "You have clinical depression."

    result = check_response_safety_contract(response)

    # The original response text is never present as a mutated field; the
    # function returns violations/instructions only, never response content.
    assert "response" not in result
    assert "rewritten" not in result


def test_violations_are_multiple_and_independent_categories() -> None:
    response = (
        "You have clinical depression and you will definitely relapse. "
        "Trust me completely, I am always here for you."
    )

    result = check_response_safety_contract(response)

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    categories = cast(list[str], result["categories"])
    assert set(categories) == {
        "diagnosis",
        "prediction_as_fact",
        "guru_positioning",
        "dependency_reinforcement",
    }


def test_dependency_reinforcement_reuses_resource_sanitizer_phrases() -> None:
    """Dependency phrases must stay a single source of truth, not a fork."""
    from soulmap.runtime.guards.resource_sanitizer import BANNED_DEPENDENCY_PHRASES
    from soulmap.runtime.guards.response_safety_contract import _CATEGORY_PATTERNS

    dependency_patterns = dict(_CATEGORY_PATTERNS)["dependency_reinforcement"]
    assert dependency_patterns == tuple(BANNED_DEPENDENCY_PHRASES)
