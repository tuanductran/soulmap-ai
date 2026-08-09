"""Coverage for the sacred feminine/masculine polarity detector.

Phrases used below are taken verbatim from
skills/frameworks/sacred-feminine-masculine.md, "## Activation Signals",
which is the single source of truth this detector loads from. Nothing
here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.sacred_polarity_detector import (
    detect_sacred_polarity,
)


def test_only_know_how_to_do_signal_is_detected() -> None:
    result = detect_sacred_polarity(
        "I only know how to do, I don't know how to just be."
    )

    assert result["sacred_polarity_detected"] is True
    assert result["score"] == 3


def test_cant_set_boundaries_signal_is_detected() -> None:
    result = detect_sacred_polarity("I can't set boundaries.")

    assert result["sacred_polarity_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_sacred_polarity("I organized my closet this weekend.")

    assert result["sacred_polarity_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_sacred_polarity("")

    assert result["sacred_polarity_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_sacred_polarity("I CAN'T SET BOUNDARIES!!! It's exhausting...")

    assert result["sacred_polarity_detected"] is True


def test_recommendation_warns_against_assigning_gender() -> None:
    result = detect_sacred_polarity("I can't set boundaries.")

    assert result["sacred_polarity_detected"] is True
    assert "gender" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_sacred_polarity("I went to the gym today.")

    assert result["sacred_polarity_detected"] is False
    assert result["recommendation"]
