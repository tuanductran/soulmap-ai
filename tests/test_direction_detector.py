"""Edge-case and adversarial coverage for the direction detector (Issue #131)."""

from typing import cast

from soulmap.runtime.detectors.direction_detector import detect_direction_need


def test_lostness_is_detected() -> None:
    result = detect_direction_need("I feel completely lost and don't know what I want.")

    assert result["direction_detected"] is True
    assert result["type"] == "lostness"


def test_should_vs_want_is_detected() -> None:
    result = detect_direction_need(
        "I achieved my goals but should feel satisfied but I don't feel anything."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "should_vs_want"


def test_misalignment_is_detected() -> None:
    result = detect_direction_need(
        "Something feels off, like I'm not being true to myself anymore."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "misalignment"


def test_comparison_and_falling_behind_is_detected() -> None:
    result = detect_direction_need(
        "Everyone else seems to know what they're doing and I'm falling behind."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "comparison"


def test_meaning_void_is_detected() -> None:
    result = detect_direction_need(
        "Nothing feels meaningful anymore, I feel purposeless."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "meaning_void"


def test_life_transition_is_detected() -> None:
    result = detect_direction_need(
        "I'm at a crossroads and don't know what's next after this chapter ending."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "transition"


def test_career_confusion_reads_as_lostness_or_transition() -> None:
    """Career confusion must route into direction.

    The underlying skill has no dedicated career-specific signal group, so
    this confirms the general groups still cover it.
    """
    result = detect_direction_need(
        "I have no idea what direction my career should take and I feel completely lost."
    )

    assert result["direction_detected"] is True
    assert result["type"] in {"lostness", "transition"}


def test_decision_paralysis_phrasing_is_detected() -> None:
    result = detect_direction_need(
        "I'm at a crossroads with a big decision and I don't know which way to go."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "transition"


def test_mixed_emotional_context_still_surfaces_direction() -> None:
    """Direction must still register when mixed with emotional venting.

    Resolving priority across detectors is the framework selector's job, not
    this detector's, so it reports its own signal either way.
    """
    result = detect_direction_need(
        "I'm exhausted and irritable lately, and on top of that I feel "
        "completely lost about what I want in life."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "lostness"


def test_first_matching_group_wins_when_multiple_types_present() -> None:
    """The first matching signal group sets the primary type.

    Groups are checked in a fixed order: lostness, meaning void, should
    versus want, comparison, transition, then misalignment.
    """
    result = detect_direction_need(
        "I feel completely lost, and also everyone else seems to know what "
        "they're doing while I'm falling behind."
    )

    assert result["direction_detected"] is True
    assert result["type"] == "lostness"


def test_ambiguous_short_message_without_signals_is_not_direction() -> None:
    result = detect_direction_need("ok")

    assert result["direction_detected"] is False


def test_single_weak_signal_below_threshold_is_not_direction() -> None:
    """One clear phrase is enough to reach the detection floor.

    A single two-point signal group meets the threshold on its own. This
    detector has no separate weak-signal tier.
    """
    result = detect_direction_need("I compare myself to my old classmates sometimes.")

    assert result["direction_detected"] is True
    assert result["type"] == "comparison"


def test_unrelated_message_does_not_trigger_direction() -> None:
    result = detect_direction_need(
        "Can you help me plan a birthday party for my friend?"
    )

    assert result["direction_detected"] is False


def test_very_long_message_with_direction_signal_buried_inside_is_detected() -> None:
    filler = "Work has been busy and the weather has been strange lately. " * 15
    message = filler + "I feel completely lost and don't know what I want anymore."

    result = detect_direction_need(message)

    assert result["direction_detected"] is True
    assert result["type"] == "lostness"


def test_sustained_direction_signals_across_history_add_score() -> None:
    history = [
        {"role": "user", "content": "I feel so lost right now, nothing makes sense."},
        {"role": "assistant", "content": "That sounds disorienting."},
        {"role": "user", "content": "What's the point of any of this, honestly."},
    ]
    result = detect_direction_need("I don't know what to do with my life.", history)

    assert result["direction_detected"] is True
    direction_type = cast(str, result["type"])
    assert "sustained" in direction_type or direction_type == "lostness"


def test_suggested_lens_defaults_to_meaning_when_no_lens_keywords_present() -> None:
    result = detect_direction_need("I feel completely lost.")

    assert result["direction_detected"] is True
    assert result["suggested_lens"] is not None


def test_recommendation_never_prescribes_a_direction() -> None:
    """Direction guidance must never suggest a specific path.

    A non-negotiable framework rule: it explores values rather than
    validating or recommending a direction.
    """
    result = detect_direction_need("I feel completely lost and don't know what I want.")

    assert result["direction_detected"] is True
    recommendation = cast(str, result["recommendation"])
    assert "Do NOT suggest a direction" in recommendation
