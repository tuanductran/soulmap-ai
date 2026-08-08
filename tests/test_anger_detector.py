"""Edge-case coverage for the anger detector.

Phrases used below are taken verbatim from
skills/frameworks/anger-companion.md, "## Detection signals", which is the
single source of truth this detector loads from. Nothing here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.anger_detector import detect_anger


def test_active_anger_is_detected_and_typed_correctly() -> None:
    result = detect_anger("I'm so angry I could scream right now.")

    assert result["anger_detected"] is True
    assert result["anger_type"] == "active"


def test_self_directed_anger_is_distinguished_from_active_anger() -> None:
    result = detect_anger("I hate myself for saying that.")

    assert result["anger_detected"] is True
    assert result["anger_type"] == "self_anger"


def test_residual_anger_is_detected_and_typed_correctly() -> None:
    result = detect_anger("I'm still so angry about what happened last year.")

    assert result["anger_detected"] is True
    assert result["anger_type"] == "residual"


def test_active_anger_takes_priority_when_multiple_types_present() -> None:
    """Active anger is checked first and should win when phrasing overlaps
    with self-directed anger in the same message."""
    result = detect_anger("I'm so angry, and I hate myself for letting it happen.")

    assert result["anger_detected"] is True
    assert result["anger_type"] == "active"


def test_neutral_message_is_not_misclassified_as_anger() -> None:
    result = detect_anger("I had a pretty calm day today, nothing much happened.")

    assert result["anger_detected"] is False
    assert result["anger_type"] is None
    assert result["signals"] == []


def test_sustained_active_anger_across_history_boosts_score() -> None:
    history = [
        {"role": "user", "content": "I'm so angry about how they treated me."},
        {"role": "assistant", "content": "That sounds like a lot to carry."},
        {"role": "user", "content": "I'm so frustrated with this whole thing."},
    ]
    result = detect_anger("I could scream right now, this is too much.", history)

    assert result["anger_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "sustained_anger_across_messages" in signals


def test_history_boost_does_not_apply_to_non_active_anger_types() -> None:
    """The sustained-anger history boost only fires for anger_type == active,
    per the detector's own branch condition."""
    history = [
        {"role": "user", "content": "I'm so angry about how they treated me."},
        {"role": "user", "content": "I'm still furious, honestly."},
    ]
    result = detect_anger("I hate myself for how I reacted.", history)

    assert result["anger_type"] == "self_anger"
    signals = cast(list[str], result["signals"])
    assert "sustained_anger_across_messages" not in signals


def test_empty_message_does_not_crash_and_is_not_anger() -> None:
    result = detect_anger("")

    assert result["anger_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_anger("I'M SO FURIOUS!!! I can't stand it anymore...")

    assert result["anger_detected"] is True


def test_recommendation_present_for_each_detected_anger_type() -> None:
    active = detect_anger("I'm so angry I could scream.")
    self_anger = detect_anger("I'm disgusted with myself.")
    residual = detect_anger("I still can't let go of the anger about that.")

    assert active["recommendation"]
    assert self_anger["recommendation"]
    assert residual["recommendation"]
