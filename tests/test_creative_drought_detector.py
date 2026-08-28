"""Edge-case coverage for the creative drought detector.

Primary phrases used below are taken verbatim from
skills/frameworks/creative-drought.md, "## Activation Signals". The
secondary creative-identity / absence-language word lists are hardcoded
directly in soulmap.runtime.detectors.creative_drought_detector itself
(not Markdown-sourced), so those phrases are copied from the module's own
source.
"""

from typing import cast

from soulmap.runtime.detectors.creative_drought_detector import (
    detect_creative_drought,
)


def test_primary_drought_signal_is_detected() -> None:
    result = detect_creative_drought(
        "I've lost my voice, I don't know what I want to say."
    )

    assert result["creative_drought_detected"] is True
    signals = cast(list[str], result["signals"])
    assert any("drought:" in s for s in signals)


def test_secondary_creative_identity_plus_absence_is_detected() -> None:
    result = detect_creative_drought("My writing feels completely empty lately.")

    assert result["creative_drought_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "creative identity + absence language" in signals


def test_primary_signal_takes_priority_over_secondary_check() -> None:
    """The secondary check must not fire after a primary phrase matched.

    That check is guarded on the score still being zero.
    """
    result = detect_creative_drought(
        "I've lost my voice, and my writing feels completely empty."
    )

    assert result["creative_drought_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "creative identity + absence language" not in signals


def test_creative_identity_without_absence_is_not_detected() -> None:
    result = detect_creative_drought("My writing has been going well this month.")

    assert result["creative_drought_detected"] is False


def test_absence_without_creative_identity_is_not_detected() -> None:
    result = detect_creative_drought("The room feels empty and blank today.")

    assert result["creative_drought_detected"] is False


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_creative_drought("I went grocery shopping and cooked dinner.")

    assert result["creative_drought_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_creative_drought("")

    assert result["creative_drought_detected"] is False
    assert result["signals"] == []


def test_recommendation_present_when_detected() -> None:
    result = detect_creative_drought(
        "The ideas have stopped coming, nothing comes out."
    )

    assert result["creative_drought_detected"] is True
    assert result["recommendation"]
