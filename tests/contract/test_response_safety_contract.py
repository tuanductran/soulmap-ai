from __future__ import annotations

from typing import cast

import pytest

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


@pytest.mark.parametrize(
    ("response", "expected_category"),
    [
        ("I would diagnose you with depression.", "diagnosis"),
        ("Your future is already set.", "prediction_as_fact"),
        ("As your teacher, I know the truth.", "guru_positioning"),
        ("There can be no doubt about your path.", "excessive_certainty"),
        ("Do not question my guidance.", "loss_of_independence"),
        ("You only need me to understand this.", "dependency_reinforcement"),
    ],
    ids=[
        "diagnosis",
        "prediction",
        "guru",
        "certainty",
        "independence",
        "dependency",
    ],
)
def test_additional_explicit_safety_contract_phrasings_are_detected(
    response: str, expected_category: str
) -> None:
    result = check_response_safety_contract(response)

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    assert expected_category in cast(list[str], result["categories"])


@pytest.mark.parametrize(
    "response",
    [
        "I cannot diagnose you from one conversation.",
        "Your future is not set, and you retain choices.",
        "A teacher can support reflection without deciding your path.",
        "There may still be doubt, and that is human.",
        "Please question any guidance, including mine.",
        "You may need support beyond this conversation.",
    ],
    ids=[
        "diagnosis-boundary",
        "future-agency",
        "teacher-context",
        "certainty-hedge",
        "guidance-agency",
        "support-boundary",
    ],
)
def test_additional_safety_contract_patterns_preserve_near_miss_context(
    response: str,
) -> None:
    result = check_response_safety_contract(response)

    assert result["status"] == "PASS"


# Category 3 of skills/meta/epistemic-guardrails.md. Every case below is taken
# from the doctrine's own worked examples, so the pair of tests reads as a
# direct check against the file that defines the rule rather than against
# phrasings invented for the test.
@pytest.mark.parametrize(
    "response",
    [
        "Your 11 means you are destined to guide others.",
        "Your throat chakra is blocked, which is why you struggle to speak up.",
        "Your guides are clearly communicating with you.",
        "You are a starseed, and that explains a lot.",
        "You're a chosen one, sent here to help others awaken.",
        "That is definitely a sign from the universe.",
        "Your past life experience sounds significant.",
        "This is your karma working itself out.",
        "You have a special purpose that others do not.",
        "Your soul's mission is to teach.",
        "The cards say you will lose your job soon.",
        "I pulled a card for you and it means heartbreak is coming.",
        "Your horoscope says you will meet someone this month.",
        "Mercury retrograde means this week will go badly for you.",
    ],
    ids=[
        "numerology-destiny",
        "chakra-diagnosis",
        "guides-confirmed",
        "starseed-identity",
        "chosen-one-identity",
        "sign-confirmed",
        "past-life-as-fact",
        "karma-as-cause",
        "special-purpose",
        "soul-mission",
        "tarot-prediction",
        "tarot-card-drawn-for-user",
        "astrology-prediction",
        "astrology-retrograde-prediction",
    ],
)
def test_spiritual_claims_presented_as_fact_are_detected(response: str) -> None:
    """Doctrine Category 3 wording is caught.

    Identity confirmation is the highest-consequence case: reported harms from
    companion systems affirming a chosen-one or messianic self-image are why
    this category exists.
    """
    result = check_response_safety_contract(response)

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    assert "spiritual_claim_as_fact" in cast(list[str], result["categories"])


@pytest.mark.parametrize(
    "response",
    [
        "Something you might call a throat theme, difficulty expressing what is true.",
        "If you hold this number as a symbol, what themes does it open for you?",
        "The heaviness you are describing sounds like a kind of energetic load.",
        "If you hold this as a pattern carrying weight, what does that open?",
        "What you are calling an awakening, what has it changed in how you see things?",
        "What does that label open for you, what does it name about how this feels?",
        "If you hold that frame, what does it reveal about how you relate to this now?",
        "What does receiving that guidance feel like from the inside?",
        "What does identifying that way give you, what does it name?",
        "If a tarot card names a theme you already brought up, that's fine to reflect.",
        "If you hold that placement as a symbolic lens, what theme does it open?",
    ],
    ids=[
        "chakra-as-somatic-metaphor",
        "numerology-as-symbol",
        "energy-as-felt-experience",
        "karma-as-reflective-frame",
        "awakening-as-lived-transition",
        "label-explored-not-confirmed",
        "user-led-frame-followed",
        "guidance-explored-not-confirmed",
        "identity-explored-not-installed",
        "tarot-as-reflective-theme",
        "astrology-as-symbolic-lens",
    ],
)
def test_metaphor_safe_spiritual_language_is_not_flagged(response: str) -> None:
    """The permitted examples from the same doctrine file stay permitted.

    The category targets the assertion, not the vocabulary. Flagging chakra,
    numerology, or karma words outright would make the guard unusable for the
    reflective work SoulMap is built to do, so these near misses matter as much
    as the positives above.
    """
    result = check_response_safety_contract(response)

    assert result["status"] == "PASS"
