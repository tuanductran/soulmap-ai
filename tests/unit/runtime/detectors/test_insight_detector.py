"""Edge-case and adversarial coverage for the insight detector (Issue #131)."""

from typing import cast

from soulmap.runtime.detectors.insight_detector import detect_insight


def test_explicit_insight_is_detected() -> None:
    """One explicit-insight phrase reaches emerging, not strong.

    A single phrase scores three, which is emerging strength. Strong requires
    stacking a second signal group.
    """
    result = detect_insight("I finally understand why I do this.")

    assert result["insight_detected"] is True
    assert result["strength"] == "emerging"


def test_explicit_insight_plus_self_application_reaches_strong() -> None:
    result = detect_insight(
        "I finally understand why I do this, and I see the pattern now."
    )

    assert result["insight_detected"] is True
    assert result["strength"] == "strong"


def test_emerging_insight_alone_is_detected_but_not_strong() -> None:
    result = detect_insight("I'm starting to see why this keeps happening.")

    assert result["insight_detected"] is True
    assert result["strength"] == "emerging"


def test_self_application_signal_is_detected() -> None:
    result = detect_insight("I see the pattern, that's exactly what happened before.")

    assert result["insight_detected"] is True


def test_post_reflection_validation_signal_is_detected() -> None:
    result = detect_insight("Yes exactly, that resonates so much.")

    assert result["insight_detected"] is True


def test_self_reflection_and_awareness_phrasing_is_detected() -> None:
    result = detect_insight("I can see now that I've been doing this my whole life.")

    assert result["insight_detected"] is True
    assert result["strength"] == "strong"


def test_pattern_recognition_phrasing_is_detected() -> None:
    result = detect_insight("That's my pattern, I do this when I feel unsafe.")

    assert result["insight_detected"] is True


def test_reflective_question_alone_without_insight_language_is_not_insight() -> None:
    """A question mark alone should not be mistaken for a realization."""
    result = detect_insight("What do you think I should do about this?")

    assert result["insight_detected"] is False


def test_philosophical_exploration_without_realization_language_is_not_insight() -> (
    None
):
    result = detect_insight("I've been thinking about what makes life meaningful.")

    assert result["insight_detected"] is False


def test_insight_type_classifies_as_noticing_earlier() -> None:
    result = detect_insight(
        "I finally understand this pattern. I want to catch it earlier next time."
    )

    assert result["insight_detected"] is True
    assert result["insight_type"] == "noticing_earlier"


def test_insight_type_classifies_as_when_it_appears() -> None:
    result = detect_insight(
        "I finally understand. When does this pattern usually show up for me?"
    )

    assert result["insight_detected"] is True
    assert result["insight_type"] == "when_it_appears"


def test_insight_type_classifies_as_different_response() -> None:
    result = detect_insight(
        "I finally get it. What could I do differently next time this happens?"
    )

    assert result["insight_detected"] is True
    assert result["insight_type"] == "different_response"


def test_insight_type_defaults_to_hold_first_with_no_secondary_cues() -> None:
    result = detect_insight("I finally understand why I do this.")

    assert result["insight_detected"] is True
    assert result["insight_type"] == "hold_first"


def test_short_validation_after_assistant_reflection_is_detected_via_history() -> None:
    history = [
        {"role": "user", "content": "I keep pulling away from people."},
        {
            "role": "assistant",
            "content": "I wonder if part of you that pulls away is trying to stay safe.",
        },
    ]
    result = detect_insight("Yes, that's it.", history)

    assert result["insight_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "validation_of_reflection" in signals


def test_long_validation_message_after_reflection_does_not_get_history_bonus() -> None:
    """The validation bonus applies only to short confirmations.

    The history-driven bonus is limited to replies under thirty words, so a
    long unrelated reply must not trigger it.
    """
    history = [
        {"role": "user", "content": "I keep pulling away from people."},
        {
            "role": "assistant",
            "content": "I wonder if part of you that pulls away is trying to stay safe.",
        },
    ]
    long_message = (
        "Yes, that's it, but I also wanted to tell you about my whole week because "
        "so much has happened and I am not sure where to start, there was work "
        "drama and family stuff and I am just overwhelmed by everything going on "
        "right now honestly."
    )
    result = detect_insight(long_message, history)

    signals = cast(list[str], result["signals"])
    assert "validation_of_reflection" not in signals


def test_ambiguous_short_message_with_no_signals_is_not_insight() -> None:
    result = detect_insight("ok")

    assert result["insight_detected"] is False


def test_unrelated_message_does_not_trigger_insight() -> None:
    result = detect_insight("Can you recommend a good book to read this weekend?")

    assert result["insight_detected"] is False


def test_very_long_message_with_insight_signal_buried_inside_is_detected() -> None:
    filler = "There has been a lot going on this week and I am quite tired. " * 15
    message = (
        filler
        + "I finally understand why I keep doing this, and I see the pattern now."
    )

    result = detect_insight(message)

    assert result["insight_detected"] is True
    assert result["strength"] == "strong"


def test_recommendation_explicitly_forbids_prescriptive_should_language() -> None:
    """Meaning integration must never prescribe.

    A non-negotiable framework rule. The recommendation legitimately names
    the banned word inside an instruction to the model, so this checks that
    the instruction is present rather than that the substring is absent.
    """
    result = detect_insight("I finally understand why I do this.")

    assert result["insight_detected"] is True
    recommendation = cast(str, result["recommendation"])
    assert "Do not use the word 'should'" in recommendation
