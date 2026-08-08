"""Edge-case coverage for the empath boundary detector.

Primary phrases used below are taken verbatim from
skills/frameworks/empath-boundary.md, "## Activation Signals". The
secondary drain/people-context word lists are hardcoded directly in
soulmap.runtime.detectors.empath_detector itself (not Markdown-sourced),
so those phrases are copied from the module's own source.
"""

from typing import cast

from soulmap.runtime.detectors.empath_detector import detect_empath_overwhelm


def test_primary_empath_signal_is_detected() -> None:
    result = detect_empath_overwhelm("I absorb everyone's emotions, it's exhausting.")

    assert result["empath_detected"] is True
    signals = cast(list[str], result["signals"])
    assert any("empath:" in s for s in signals)


def test_secondary_drain_plus_people_context_is_detected() -> None:
    result = detect_empath_overwhelm("I feel so drained after being around people.")

    assert result["empath_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "drain + people context" in signals


def test_primary_signal_takes_priority_over_secondary_check() -> None:
    """The secondary drain+people check is guarded by `score == 0`, so it
    should not fire once a primary phrase has already matched."""
    result = detect_empath_overwhelm(
        "I absorb everyone's emotions and feel drained after being around people."
    )

    assert result["empath_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "drain + people context" not in signals


def test_drain_without_people_context_is_not_detected() -> None:
    result = detect_empath_overwhelm("I feel drained today for no particular reason.")

    assert result["empath_detected"] is False


def test_people_context_without_drain_is_not_detected() -> None:
    result = detect_empath_overwhelm("I was around people at work today.")

    assert result["empath_detected"] is False


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_empath_overwhelm("I read a book and went to bed early.")

    assert result["empath_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_empath_overwhelm("")

    assert result["empath_detected"] is False
    assert result["signals"] == []


def test_recommendation_present_when_detected() -> None:
    result = detect_empath_overwhelm("I don't know which feelings are mine anymore.")

    assert result["empath_detected"] is True
    assert result["recommendation"]
