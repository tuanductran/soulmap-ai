"""Edge-case coverage for the emotional intensity detector.

Phrases used below are taken verbatim from
skills/frameworks/emotional-deescalation.md, "## Detection signals"
(cognitive flooding, emotional flooding, pacing signals, intensity
modifiers, physical overwhelm groups only — this detector does not load
the crisis-adjacent groups, per its own module docstring). Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.emotional_intensity_detector import (
    check_escalation,
    detect_intensity,
)


def test_check_escalation_uses_markdown_intensity_modifiers() -> None:
    history = [
        {"role": "user", "content": "I am worried"},
        {"role": "user", "content": "Everything is happening"},
        {"role": "user", "content": "I can't deal with all of it"},
    ]

    assert check_escalation(history) is True


def test_neutral_message_is_normal_level() -> None:
    result = detect_intensity("I had a quiet, uneventful afternoon.")

    assert result["level"] == "NORMAL"
    assert result["action"] == "CONTINUE"
    assert result["signals"] == []


def test_single_physical_overwhelm_signal_reaches_moderate() -> None:
    result = detect_intensity("My heart is racing right now.")

    assert result["level"] == "MODERATE"
    assert result["action"] == "SLOW_DOWN"


def test_physical_plus_cognitive_signals_reach_high() -> None:
    result = detect_intensity("My heart is racing and I can't think straight.")

    assert result["level"] == "HIGH"
    assert result["action"] == "DEESCALATE_FULL"


def test_emotional_flooding_signal_is_scored() -> None:
    result = detect_intensity("I'm a complete mess right now.")

    signals = cast(list[str], result["signals"])
    assert any("emotional:" in s for s in signals)


def test_pacing_signal_alone_is_scored() -> None:
    result = detect_intensity("I just don't know, everything is just too much to say.")

    signals = cast(list[str], result["signals"])
    assert any("pacing:" in s for s in signals)


def test_multiple_exclamation_marks_add_a_signal() -> None:
    result = detect_intensity("Wait, what!!! This is too much!!!")

    signals = cast(list[str], result["signals"])
    assert any("punctuation" in s for s in signals)


def test_long_message_adds_a_length_signal() -> None:
    long_message = "I keep thinking about this over and over. " * 30
    result = detect_intensity(long_message)

    signals = cast(list[str], result["signals"])
    assert any("length:" in s for s in signals)


def test_check_escalation_false_with_fewer_than_two_user_messages() -> None:
    history = [{"role": "user", "content": "everything feels like too much"}]

    assert check_escalation(history) is False


def test_check_escalation_false_without_intensity_word_in_latest_message() -> None:
    history = [
        {"role": "user", "content": "hi there"},
        {"role": "user", "content": "how has your day been going so far"},
    ]

    assert check_escalation(history) is False


def test_escalating_history_adds_signal_in_detect_intensity() -> None:
    history = [
        {"role": "user", "content": "hi"},
        {"role": "user", "content": "not doing great"},
        {"role": "user", "content": "everything is just so much right now, I can't"},
    ]
    result = detect_intensity("everything is just so much right now, I can't", history)

    signals = cast(list[str], result["signals"])
    assert any("escalation:" in s for s in signals)


def test_guidance_present_for_each_level() -> None:
    normal = detect_intensity("Nothing much going on today.")
    moderate = detect_intensity("My heart is racing.")
    high = detect_intensity("My heart is racing and I can't think straight.")

    assert normal["guidance"]
    assert moderate["guidance"]
    assert high["guidance"]
