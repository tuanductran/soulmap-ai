"""Edge-case coverage for the perfectionism paralysis detector.

Phrases used below are taken verbatim from
skills/frameworks/perfectionism-paralysis.md ("## Activation Signals") and
skills/frameworks/shadow-patterns.md ("### Perfectionism (as protection)"),
the two sources this detector loads from. Nothing here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.perfectionism_paralysis_detector import (
    detect_perfectionism_paralysis,
)


def test_paralysis_signal_is_detected() -> None:
    result = detect_perfectionism_paralysis(
        "It's never ready, nothing is ever good enough."
    )

    assert result["perfectionism_paralysis_detected"] is True
    signals = cast(list[str], result["signals"])
    assert any("paralysis:" in s for s in signals)


def test_general_perfectionism_signal_alone_does_not_trigger_detection() -> None:
    """Doctrine (perfectionism-paralysis.md, "Distinguish from genuine
    discernment"): "Perfectionism paralysis is a pattern, not a single
    instance." A bare generic signal with no repetition evidence must stay
    below threshold, not promote to primary_framework on one message."""
    result = detect_perfectionism_paralysis("People never meet my standards.")

    assert result["perfectionism_paralysis_detected"] is False
    signals = cast(list[str], result["signals"])
    assert signals == ["perfectionism: 'people never meet my standards.'"]


def test_general_perfectionism_signal_with_history_repetition_is_detected() -> None:
    """The generic signal only crosses the threshold once combined with the
    history repetition bonus - the actual "pattern, not a single instance"
    check the doctrine asks for."""
    history = [
        {"role": "user", "content": "I'm still not ready to share this."},
    ]
    result = detect_perfectionism_paralysis("People never meet my standards.", history)

    assert result["perfectionism_paralysis_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "perfectionism: 'people never meet my standards.'" in signals
    assert "pattern_persistence_in_history" in signals


def test_general_perfectionism_signal_with_self_reported_repetition_is_detected() -> (
    None
):
    """Repetition evidence can also come from the current message itself
    naming its own repetition, not only from prior history turns."""
    result = detect_perfectionism_paralysis(
        "I almost sent it a hundred times. It is never good enough to send."
    )

    assert result["perfectionism_paralysis_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "pattern_persistence_in_message" in signals


def test_paralysis_signal_takes_priority_over_general_signal() -> None:
    """The paralysis loop runs first and sets score > 0, so the general
    perfectionism loop (guarded by `score == 0`) should not also fire."""
    result = detect_perfectionism_paralysis(
        "It's never ready, and honestly nothing is ever good enough."
    )

    assert result["perfectionism_paralysis_detected"] is True
    signals = cast(list[str], result["signals"])
    assert not any(s.startswith("perfectionism:") for s in signals)


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_perfectionism_paralysis(
        "I finished the report and sent it this morning."
    )

    assert result["perfectionism_paralysis_detected"] is False
    assert result["signals"] == []


def test_pattern_persistence_in_history_boosts_score() -> None:
    history = [
        {"role": "user", "content": "I'm still not ready to share this."},
        {"role": "assistant", "content": "That's understandable."},
    ]
    result = detect_perfectionism_paralysis("It's never ready, honestly.", history)

    assert result["perfectionism_paralysis_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "pattern_persistence_in_history" in signals


def test_history_does_not_boost_when_no_current_signal_present() -> None:
    """The history check only runs when score > 0 from the current message."""
    history = [
        {"role": "user", "content": "I'm still not ready to share this."},
    ]
    result = detect_perfectionism_paralysis("I went for a walk today.", history)

    assert result["perfectionism_paralysis_detected"] is False
    signals = cast(list[str], result["signals"])
    assert "pattern_persistence_in_history" not in signals


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_perfectionism_paralysis("")

    assert result["perfectionism_paralysis_detected"] is False
    assert result["signals"] == []


def test_recommendation_present_when_detected() -> None:
    result = detect_perfectionism_paralysis("I can never finish anything.")

    assert result["perfectionism_paralysis_detected"] is True
    assert result["recommendation"]


def test_neutral_history_does_not_add_persistence_signal() -> None:
    history = [{"role": "user", "content": "I took a walk this morning."}]

    result = detect_perfectionism_paralysis("It's never ready, honestly.", history)

    assert result["perfectionism_paralysis_detected"] is True
    assert result["score"] == 3
    signals = cast(list[str], result["signals"])
    assert "pattern_persistence_in_history" not in signals
