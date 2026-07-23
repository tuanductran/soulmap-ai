"""Edge-case and adversarial coverage for the grief detector (Issue #131)."""

from typing import cast

from soulmap.runtime.detectors.grief_detector import detect_grief


def test_acute_grief_is_detected_and_typed_correctly() -> None:
    result = detect_grief("My mother died yesterday. I still cannot believe it.")

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_anticipatory_grief_is_distinguished_from_acute_grief() -> None:
    result = detect_grief("I've been watching my father decline for months now.")

    assert result["grief_detected"] is True
    assert result["grief_type"] == "anticipatory"


def test_ambiguous_loss_is_detected_and_typed_correctly() -> None:
    result = detect_grief(
        "No one understands why I'm upset about this, and I don't know if "
        "I'm allowed to grieve since it was just a friendship that ended."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "ambiguous"


def test_complicated_grief_is_detected_and_typed_correctly() -> None:
    result = detect_grief(
        "I feel guilty that I feel relieved, and now I have complicated "
        "feelings about their death since our relationship was toxic and "
        "abusive."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "complicated"


def test_acute_grief_takes_priority_when_multiple_types_present() -> None:
    """Acute grief is checked first and should win when phrasing overlaps."""
    result = detect_grief(
        "My partner died last week and I feel guilty that I feel relieved."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_sadness_alone_is_not_misclassified_as_grief() -> None:
    """A generic sad mood, with no loss language, should not trigger grief."""
    result = detect_grief("I've been feeling really down and sad the past few days.")

    assert result["grief_detected"] is False


def test_grief_mixed_with_anxiety_still_registers_as_grief() -> None:
    result = detect_grief(
        "My mother died last month and now I'm anxious all the time, like "
        "something else terrible is about to happen."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_grief_mixed_with_spiritual_questions_still_registers_as_grief() -> None:
    result = detect_grief(
        "My father died three days ago and I keep wondering if there's any "
        "meaning or purpose behind any of this."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_grief_plus_direction_seeking_still_registers_as_grief() -> None:
    """Grief language plus life-direction language: grief must still surface;
    routing priority (grief blocks direction) is verified separately at the
    framework-selector level."""
    result = detect_grief(
        "My mother died last month and now I have no idea what direction my "
        "life is going in without her."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_sustained_grief_across_history_boosts_score() -> None:
    history = [
        {"role": "user", "content": "He died last week and I can't stop crying."},
        {"role": "assistant", "content": "That sounds heavy to carry."},
        {
            "role": "user",
            "content": "My mother died a few years ago too, and this brings it all back.",
        },
    ]
    result = detect_grief("I don't know how to do this without them.", history)

    assert result["grief_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "sustained_grief_across_messages" in signals


def test_empty_message_does_not_crash_and_is_not_grief() -> None:
    result = detect_grief("")

    assert result["grief_detected"] is False
    assert result["signals"] == []


def test_very_long_message_with_grief_signal_buried_inside_is_detected() -> None:
    filler = "I've had a long week at work and a lot has been going on. " * 20
    message = filler + "Also, my mother died yesterday and I don't know what to do."

    result = detect_grief(message)

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_grief("MY DOG DIED!!! I can't believe it, still in shock...")

    assert result["grief_detected"] is True


def test_bare_word_grief_is_classified_acute_not_by_context() -> None:
    """Detector boundary finding: 'grief' itself is in the acute-signal list
    and acute is checked first, so any mention of the bare word 'grief' is
    classified as acute regardless of the surrounding context describing a
    more ambiguous or complicated loss. This is documented existing behavior,
    not something this test suite changes."""
    result = detect_grief(
        "I don't know if this counts as real grief since it was just a "
        "friendship that ended, not a death."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_near_miss_phrasing_without_loss_language_is_not_grief() -> None:
    """Adjacent-but-different wording (e.g. general worry about a pet) should
    not falsely trigger grief detection."""
    result = detect_grief("I'm worried my dog might be getting sick soon.")

    assert result["grief_detected"] is False
