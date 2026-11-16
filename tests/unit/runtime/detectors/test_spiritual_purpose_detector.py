"""Coverage for the spiritual purpose detector.

Phrases used below are taken verbatim from
skills/frameworks/spiritual-purpose.md, "## Activation Signals", which is
the single source of truth this detector loads from. Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.spiritual_purpose_detector import (
    detect_spiritual_purpose,
)


def test_calling_or_should_signal_is_detected() -> None:
    result = detect_spiritual_purpose(
        "I don't know if this is my calling or just what I think I should do."
    )

    assert result["spiritual_purpose_detected"] is True
    assert result["score"] == 3


def test_waiting_for_certainty_signal_is_detected() -> None:
    result = detect_spiritual_purpose("I'm waiting for certainty before I act.")

    assert result["spiritual_purpose_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_spiritual_purpose("I picked up my kids from school.")

    assert result["spiritual_purpose_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_spiritual_purpose("")

    assert result["spiritual_purpose_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_spiritual_purpose("I'M WAITING FOR CERTAINTY BEFORE I ACT!!!")

    assert result["spiritual_purpose_detected"] is True


def test_recommendation_warns_against_telling_user_their_purpose() -> None:
    result = detect_spiritual_purpose("I'm waiting for certainty before I act.")

    assert result["spiritual_purpose_detected"] is True
    assert "never tell the user" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_spiritual_purpose("I did laundry today.")

    assert result["spiritual_purpose_detected"] is False
    assert result["recommendation"]
