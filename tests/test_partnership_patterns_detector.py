"""Coverage for the partnership patterns detector.

Phrases used below are taken verbatim from
skills/soulmate/partnership-patterns.md, "## Activation Signals", which is
the single source of truth this detector loads from. Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.partnership_patterns_detector import (
    detect_partnership_patterns,
)


def test_keep_dating_same_type_signal_is_detected() -> None:
    result = detect_partnership_patterns("I keep dating the same type of person.")

    assert result["partnership_pattern_detected"] is True
    assert result["score"] == 3


def test_pull_away_signal_is_detected() -> None:
    result = detect_partnership_patterns(
        "I pull away right when things start going well."
    )

    assert result["partnership_pattern_detected"] is True


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_partnership_patterns("I finished a report at work today.")

    assert result["partnership_pattern_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_partnership_patterns("")

    assert result["partnership_pattern_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_partnership_patterns(
        "I KEEP DATING THE SAME TYPE OF PERSON!!! it happens every time..."
    )

    assert result["partnership_pattern_detected"] is True


def test_recommendation_keeps_lens_inward() -> None:
    result = detect_partnership_patterns("I keep dating the same type of person.")

    assert result["partnership_pattern_detected"] is True
    assert "inward" in cast(str, result["recommendation"]).lower()


def test_recommendation_present_when_not_detected() -> None:
    result = detect_partnership_patterns("I watched TV tonight.")

    assert result["partnership_pattern_detected"] is False
    assert result["recommendation"]
