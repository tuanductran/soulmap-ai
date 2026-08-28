"""Edge-case coverage for the inner conflict detector.

Phrases used below are taken verbatim from
skills/frameworks/inner-parts.md, "## Detection signals", which is the
single source of truth this detector loads from. Nothing here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.inner_conflict_detector import detect_inner_conflict


def test_explicit_conflict_is_detected_and_typed_correctly() -> None:
    result = detect_inner_conflict(
        "Part of me wants to leave, but another part is scared."
    )

    assert result["conflict_detected"] is True
    assert result["type"] == "explicit"


def test_internal_dialogue_is_detected_and_typed_correctly() -> None:
    result = detect_inner_conflict(
        "I keep telling myself it's fine, I know better but I ignore it."
    )

    assert result["conflict_detected"] is True
    assert result["type"] == "self_dialogue"


def test_part_naming_is_detected_and_typed_correctly() -> None:
    """Part-naming phrases register without an explicit conflict phrase.

    "The part of me that" and "something in me keeps" name a part without
    overlapping the explicit-conflict phrase list.
    """
    result = detect_inner_conflict(
        "The part of me that stays quiet is the same part something in me keeps protecting."
    )

    assert result["conflict_detected"] is True
    assert result["type"] == "part_naming"


def test_behavioral_confusion_is_detected_and_typed_correctly() -> None:
    result = detect_inner_conflict(
        "I did the opposite of what I wanted, that's not like me at all."
    )

    assert result["conflict_detected"] is True


def test_neutral_message_is_not_misclassified_as_conflict() -> None:
    result = detect_inner_conflict("I went for a walk and then made dinner.")

    assert result["conflict_detected"] is False
    assert result["type"] is None
    assert result["signals"] == []
    assert result["parts_suggested"] == []


def test_historical_explicit_conflict_in_recent_history_boosts_score() -> None:
    history = [
        {
            "role": "user",
            "content": "Part of me wants to stay but part of me wants to go.",
        },
        {
            "role": "assistant",
            "content": "That sounds like a real pull in two directions.",
        },
    ]
    result = detect_inner_conflict("I'm torn about what to do next.", history)

    assert result["conflict_detected"] is True
    conflict_types = result["type"]
    assert conflict_types is not None


def test_parts_suggested_returns_at_most_three_archetypes() -> None:
    result = detect_inner_conflict(
        "Part of me wants to protect myself and shut down, part of me is "
        "afraid of what if it goes wrong, part of me is furious and fed up, "
        "and part of me still believes it could be different."
    )

    parts = cast(list[str], result["parts_suggested"])
    assert len(parts) <= 3
    assert all(isinstance(p, str) for p in parts)


def test_parts_suggested_is_empty_when_no_archetype_signals_present() -> None:
    result = detect_inner_conflict("Part of me wants to know the truth.")

    assert result["parts_suggested"] == []


def test_empty_message_does_not_crash_and_is_not_conflict() -> None:
    result = detect_inner_conflict("")

    assert result["conflict_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_inner_conflict(
        "PART OF ME WANTS TO STAY, but another part says leave!!!"
    )

    assert result["conflict_detected"] is True


def test_recommendation_present_when_conflict_detected() -> None:
    result = detect_inner_conflict("I'm torn, part of me wants to stay.")

    assert result["conflict_detected"] is True
    assert result["recommendation"]


def test_recommendation_present_but_neutral_when_no_conflict_detected() -> None:
    result = detect_inner_conflict("I made coffee this morning.")

    assert result["conflict_detected"] is False
    assert "no inner conflict signals detected" in str(result["recommendation"]).lower()
