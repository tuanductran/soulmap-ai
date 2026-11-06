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
    """Grief must still surface alongside life-direction language.

    Routing priority, where grief blocks direction, is verified separately at
    the framework-selector level.
    """
    result = detect_grief(
        "My mother died last month and now I have no idea what direction my "
        "life is going in without her."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_acute_exchange_count_starts_at_first_acute_grief_signal() -> None:
    history = [
        {"role": "user", "content": "I had a difficult week at work."},
        {"role": "assistant", "content": "That sounds tiring."},
        {"role": "user", "content": "My mother died last week."},
        {"role": "assistant", "content": "I am sorry for your loss."},
        {
            "role": "user",
            "content": "My dog died yesterday, and I keep remembering her voice.",
        },
    ]

    result = detect_grief("I have been thinking about what she meant to me.", history)

    assert result["grief_detected"] is True
    assert result["acute_exchange_count"] == 3


def test_acute_exchange_count_does_not_include_pre_grief_messages() -> None:
    history = [
        {"role": "user", "content": "I had a difficult week at work."},
        {"role": "user", "content": "My mother died last week."},
        {
            "role": "user",
            "content": "My dog died yesterday, and I keep remembering her voice.",
        },
    ]

    result = detect_grief("I have been thinking about what she meant to me.", history)

    assert result["grief_detected"] is True
    assert result["acute_exchange_count"] == 3


def test_acute_exchange_count_does_not_include_unrelated_current_turn() -> None:
    history = [
        {"role": "user", "content": "My mother died last week."},
        {"role": "user", "content": "I miss her so much."},
    ]

    result = detect_grief("Can you help me plan a work presentation?", history)

    # Sustained grief can still be detected from history, but an unrelated
    # current turn must not advance the active acute-grief exchange count.
    assert result["grief_detected"] is True
    assert result["acute_exchange_count"] == 2


def test_acute_exchange_count_resets_after_unrelated_user_turns() -> None:
    history = [
        {"role": "user", "content": "My mother died last week."},
        {"role": "user", "content": "I miss her so much."},
        {"role": "user", "content": "Can you help me plan a work presentation?"},
    ]

    result = detect_grief("My dog died yesterday, and I feel lost.", history)

    assert result["grief_detected"] is True
    assert result["acute_exchange_count"] == 1


def test_grief_specific_readiness_is_loaded_from_markdown() -> None:
    result = detect_grief("I've been thinking about what she meant to me.")

    assert result["readiness_detected"] is True


def test_acute_exchange_count_survives_the_recent_scoring_window() -> None:
    history = [
        {"role": "user", "content": "My mother died last week."},
        {"role": "assistant", "content": "I am sorry for your loss."},
        {"role": "user", "content": "I miss her so much."},
        {"role": "user", "content": "I still cannot believe she is gone."},
        {"role": "user", "content": "I can't accept it."},
        {"role": "user", "content": "I am still in shock."},
        {"role": "user", "content": "I don't know how to do this without her."},
    ]

    result = detect_grief(
        "My mother died last week, and I have been thinking about what she meant to me.",
        history,
    )

    assert result["grief_detected"] is True
    assert result["acute_exchange_count"] == 7


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
    """The bare word "grief" always classifies as acute.

    A detector boundary finding: "grief" is itself in the acute-signal list
    and acute is checked first, so the word alone reads as acute regardless
    of surrounding context describing a more ambiguous or complicated loss.
    This documents existing behavior rather than asserting it is ideal.
    """
    result = detect_grief(
        "I don't know if this counts as real grief since it was just a "
        "friendship that ended, not a death."
    )

    assert result["grief_detected"] is True
    assert result["grief_type"] == "acute"


def test_near_miss_phrasing_without_loss_language_is_not_grief() -> None:
    """Adjacent wording must not falsely trigger grief.

    General worry about a pet, for example, is not a loss signal.
    """
    result = detect_grief("I'm worried my dog might be getting sick soon.")

    assert result["grief_detected"] is False
