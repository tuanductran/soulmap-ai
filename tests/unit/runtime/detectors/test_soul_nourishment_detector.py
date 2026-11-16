"""Coverage for the soul nourishment detector.

Phrases used below are taken verbatim from
skills/frameworks/soul-nourishment.md, "## Activation Signals", which is
the single source of truth this detector loads from. Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.soul_nourishment_detector import (
    detect_soul_nourishment,
)


def test_feeds_my_soul_signal_is_detected() -> None:
    result = detect_soul_nourishment(
        "This feeds my soul, being in nature makes me feel alive."
    )

    assert result["soul_nourishment_detected"] is True
    assert result["score"] == 3


def test_confuses_busy_with_nourishment_signal_is_detected() -> None:
    result = detect_soul_nourishment("I confuse being busy with taking care of myself.")

    assert result["soul_nourishment_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_soul_nourishment("I finished a report at work today.")

    assert result["soul_nourishment_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_soul_nourishment("")

    assert result["soul_nourishment_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_soul_nourishment(
        "THIS FEEDS MY SOUL!!! I feel so alive right now..."
    )

    assert result["soul_nourishment_detected"] is True


def test_recommendation_warns_against_prescribing_practices() -> None:
    result = detect_soul_nourishment(
        "This feeds my soul, being in nature makes me feel alive."
    )

    assert result["soul_nourishment_detected"] is True
    assert "prescribe" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_soul_nourishment("I watched TV tonight.")

    assert result["soul_nourishment_detected"] is False
    assert result["recommendation"]
