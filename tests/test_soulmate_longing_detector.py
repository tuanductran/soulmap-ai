"""Coverage for the soulmate longing detector.

Phrases used below are taken verbatim from skills/soulmate/soulmate-longing.md,
"## Activation Signals", which is the single source of truth this detector
loads from. Nothing here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.soulmate_longing_detector import (
    detect_soulmate_longing,
)


def test_never_find_soulmate_signal_is_detected() -> None:
    result = detect_soulmate_longing("I feel like i'll never find my soulmate.")

    assert result["soulmate_longing_detected"] is True
    assert result["score"] == 3


def test_thought_he_was_the_one_signal_is_detected() -> None:
    result = detect_soulmate_longing("I thought he was the one and I was so wrong.")

    assert result["soulmate_longing_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_soulmate_longing("I finished a report at work today.")

    assert result["soulmate_longing_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_soulmate_longing("")

    assert result["soulmate_longing_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_soulmate_longing(
        "I'LL NEVER FIND MY SOULMATE!!! everyone else has found their soulmate..."
    )

    assert result["soulmate_longing_detected"] is True


def test_recommendation_warns_against_confirming_identity() -> None:
    result = detect_soulmate_longing("I'll never find my soulmate.")

    assert result["soulmate_longing_detected"] is True
    assert "confirm" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_soulmate_longing("I watered the plants tonight.")

    assert result["soulmate_longing_detected"] is False
    assert result["recommendation"]
