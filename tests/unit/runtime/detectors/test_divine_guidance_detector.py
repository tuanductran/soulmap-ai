"""Coverage for the divine guidance detector.

Phrases used below are taken verbatim from
skills/frameworks/divine-guidance.md, "## Activation Signals", which is
the single source of truth this detector loads from. Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.divine_guidance_detector import (
    detect_divine_guidance,
)


def test_intuition_or_fear_signal_is_detected() -> None:
    result = detect_divine_guidance("I don't know if this is intuition or fear.")

    assert result["divine_guidance_detected"] is True
    assert result["score"] == 3


def test_dont_trust_intuition_signal_is_detected() -> None:
    result = detect_divine_guidance("I don't trust my own intuition.")

    assert result["divine_guidance_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_divine_guidance("I booked a dentist appointment for next week.")

    assert result["divine_guidance_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_divine_guidance("")

    assert result["divine_guidance_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_divine_guidance("I DON'T KNOW IF THIS IS INTUITION OR FEAR!!!")

    assert result["divine_guidance_detected"] is True


def test_recommendation_warns_against_confirming_guidance() -> None:
    result = detect_divine_guidance("I don't know if this is intuition or fear.")

    assert result["divine_guidance_detected"] is True
    assert "never confirm" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_divine_guidance("I bought groceries today.")

    assert result["divine_guidance_detected"] is False
    assert result["recommendation"]
