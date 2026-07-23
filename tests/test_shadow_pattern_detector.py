"""Edge-case and adversarial coverage for the shadow pattern detector (Issue #131)."""

from typing import cast

from soulmap.runtime.detectors.shadow_pattern_detector import detect_shadow_patterns


def test_avoidance_pattern_is_detected() -> None:
    result = detect_shadow_patterns("I never confront anything, I just avoid it.")

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "avoidance" in patterns_found


def test_people_pleasing_pattern_is_detected() -> None:
    result = detect_shadow_patterns(
        "I can't say no to people and always end up resenting it."
    )

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "people_pleasing" in patterns_found


def test_overthinking_pattern_is_detected() -> None:
    result = detect_shadow_patterns("I replay conversations over and over in my head.")

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "overthinking" in patterns_found


def test_withdrawal_pattern_is_detected() -> None:
    result = detect_shadow_patterns(
        "When it gets too much I just go quiet and shut down."
    )

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "withdrawal" in patterns_found


def test_perfectionism_pattern_is_detected() -> None:
    result = detect_shadow_patterns(
        "Nothing is ever good enough, it has to be perfect."
    )

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "perfectionism" in patterns_found


def test_repeated_unhealthy_external_pattern_is_flagged() -> None:
    result = detect_shadow_patterns(
        "People always take advantage of me, it keeps happening."
    )

    assert result["shadow_detected"] is True
    assert result["is_external_frustration"] is True


def test_external_frustration_without_named_pattern_gives_gentle_exploration() -> None:
    """When only the external-repeat signal fires (no specific protective
    pattern), the detector should not name a pattern - it should stay in
    exploratory projection-principle territory."""
    result = detect_shadow_patterns("They always do this to me, every single time.")

    assert result["shadow_detected"] is True
    assert result["patterns_found"] == []
    assert result["is_external_frustration"] is True
    recommendation = cast(str, result["recommendation"])
    assert "projection principle" in recommendation


def test_multiple_patterns_can_be_detected_simultaneously() -> None:
    result = detect_shadow_patterns(
        "I can't say no to people, and honestly I also just go quiet and shut "
        "down when things get too intense."
    )

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "people_pleasing" in patterns_found
    patterns_found = cast(list[str], result["patterns_found"])
    assert "withdrawal" in patterns_found


def test_self_criticism_signal_is_appended_when_present() -> None:
    result = detect_shadow_patterns(
        "I always avoid conflict, I never confront anything, and honestly I hate myself for it."
    )

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "self_criticism" in patterns_found


def test_projection_language_alone_does_not_overclaim_a_pattern() -> None:
    """Inner-conflict-adjacent venting about other people, without any of the
    detector's specific protective-pattern phrases, should not fabricate a
    named pattern."""
    result = detect_shadow_patterns("My coworker really annoyed me today.")

    assert result["shadow_detected"] is False


def test_resistance_to_change_via_perfectionism_language() -> None:
    result = detect_shadow_patterns("I can't start until I know I can do it right.")

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "perfectionism" in patterns_found


def test_ambiguous_short_message_is_not_shadow() -> None:
    result = detect_shadow_patterns("ok")

    assert result["shadow_detected"] is False


def test_recommendation_uses_possibility_language_not_accusation() -> None:
    """Non-negotiable framework rule: shadow reflections are framed as
    possibility only, never as fact or accusation."""
    result = detect_shadow_patterns("I never confront anything, I just avoid it.")

    assert result["shadow_detected"] is True
    recommendation = cast(str, result["recommendation"])
    assert "Do NOT accuse" in recommendation
    recommendation = cast(str, result["recommendation"])
    assert "possibility" in recommendation.lower()


def test_recommendation_returns_ownership_after_reflection() -> None:
    result = detect_shadow_patterns(
        "I can't say no to people and always end up resenting it."
    )

    assert result["shadow_detected"] is True
    recommendation = cast(str, result["recommendation"])
    assert "Return ownership" in recommendation


def test_very_long_message_with_shadow_signal_buried_inside_is_detected() -> None:
    filler = "Today was a fairly ordinary day, nothing special happened at all. " * 15
    message = filler + "I never confront anything, I just avoid it every time."

    result = detect_shadow_patterns(message)

    assert result["shadow_detected"] is True
    patterns_found = cast(list[str], result["patterns_found"])
    assert "avoidance" in patterns_found


def test_sustained_external_frustration_across_history_is_flagged() -> None:
    history = [
        {"role": "user", "content": "People always take advantage of me at work."},
        {
            "role": "assistant",
            "content": "That sounds frustrating to keep experiencing.",
        },
        {
            "role": "user",
            "content": "Everyone always does this to me, no matter what job I'm in.",
        },
    ]
    result = detect_shadow_patterns("I don't know why this keeps happening.", history)

    assert result["shadow_detected"] is True
    assert result["is_external_frustration"] is True


def test_unrelated_message_does_not_trigger_shadow() -> None:
    result = detect_shadow_patterns("What's a good recipe for dinner tonight?")

    assert result["shadow_detected"] is False
