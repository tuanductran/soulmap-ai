"""Coverage for the Dark Night of the Soul detector.

Phrases used below are taken verbatim from
skills/frameworks/dark-night-of-soul.md, "## Activation Signals", which is
the single source of truth this detector loads from. Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.dark_night_detector import detect_dark_night


def test_spiritual_emptiness_signal_is_detected() -> None:
    result = detect_dark_night(
        "I feel spiritually empty and disconnected from everything I used to believe."
    )

    assert result["dark_night_detected"] is True
    assert result["score"] == 3


def test_lost_faith_signal_is_detected() -> None:
    result = detect_dark_night("I've lost my faith, nothing feels sacred anymore.")

    assert result["dark_night_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_dark_night("I went for a walk and made dinner tonight.")

    assert result["dark_night_detected"] is False
    assert result["score"] == 0
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_dark_night("")

    assert result["dark_night_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_dark_night("I FEEL SPIRITUALLY EMPTY!!! Nothing makes sense...")

    assert result["dark_night_detected"] is True


def test_recommendation_warns_against_premature_reassurance() -> None:
    result = detect_dark_night(
        "I feel spiritually empty and disconnected from everything."
    )

    assert result["dark_night_detected"] is True
    assert "reassurance" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_dark_night("I had coffee this morning.")

    assert result["dark_night_detected"] is False
    assert result["recommendation"]
