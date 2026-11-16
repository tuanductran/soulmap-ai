"""Edge-case coverage for the existential detector.

Phrases used below are taken verbatim from
skills/frameworks/existential-companion.md, "## Detection signals", which
is the single source of truth this detector loads from. Nothing here is
guessed.
"""

from typing import cast

from soulmap.runtime.detectors.existential_detector import detect_existential


def test_identity_shift_territory_is_detected_and_classified() -> None:
    result = detect_existential("I don't recognize myself anymore, I've lost myself.")

    assert result["existential_detected"] is True
    assert result["territory"] == "identity_shift"


def test_larger_questions_territory_is_detected_and_classified() -> None:
    result = detect_existential(
        "Nothing lasts, everything ends, and I'm aware I'm going to die."
    )

    assert result["existential_detected"] is True
    assert result["territory"] == "larger_questions"


def test_endings_grief_territory_is_detected_and_classified() -> None:
    result = detect_existential(
        "A chapter of my life is ending and I'm grieving who I was."
    )

    assert result["existential_detected"] is True
    assert result["territory"] == "endings_grief"


def test_meaning_depth_territory_is_detected_and_classified() -> None:
    result = detect_existential(
        "What is the point of any of this, why does any of this matter."
    )

    assert result["existential_detected"] is True
    assert result["territory"] == "meaning_depth"


def test_holding_territory_is_detected_and_classified() -> None:
    result = detect_existential(
        "I've been sitting with this question, I'm not looking for a solution."
    )

    assert result["existential_detected"] is True
    assert result["territory"] == "holding"


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_existential("I'm making dinner and then watching a show tonight.")

    assert result["existential_detected"] is False
    assert result["territory"] is None
    assert result["signals"] == []


def test_sustained_existential_territory_across_history_boosts_score() -> None:
    history = [
        {"role": "user", "content": "I don't recognize myself anymore."},
        {"role": "assistant", "content": "That sounds disorienting."},
        {"role": "user", "content": "What is the point of all this, honestly."},
    ]
    result = detect_existential("Who am I anymore, I don't know.", history)

    assert result["existential_detected"] is True
    signals = cast(list[str], result["signals"])
    assert any("sustained" in s for s in signals)


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_existential("")

    assert result["existential_detected"] is False
    assert result["signals"] == []


def test_recommendation_mentions_the_classified_territory() -> None:
    result = detect_existential("I don't recognize myself anymore, I've lost myself.")

    assert result["existential_detected"] is True
    assert "identity_shift" in cast(str, result["recommendation"])
