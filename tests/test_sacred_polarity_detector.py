"""Coverage for the sacred feminine/masculine polarity detector.

Phrases used below are taken verbatim from
skills/frameworks/sacred-feminine-masculine.md, "## Activation Signals",
which is the single source of truth this detector loads from. Nothing
here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.sacred_polarity_detector import (
    detect_sacred_polarity,
)


def test_only_know_how_to_do_signal_is_detected() -> None:
    result = detect_sacred_polarity(
        "I value the balance of receptivity and action. "
        "I only know how to do, I don't know how to just be."
    )

    assert result["sacred_polarity_detected"] is True
    assert result["score"] == 3


def test_boundary_difficulty_without_polarity_framing_is_not_detected() -> None:
    result = detect_sacred_polarity("I can't set boundaries.")

    assert result["sacred_polarity_detected"] is False


def test_neutral_message_is_not_misclassified() -> None:
    result = detect_sacred_polarity("I organized my closet this weekend.")

    assert result["sacred_polarity_detected"] is False
    assert result["signals"] == []


def test_empty_message_does_not_crash_and_is_not_detected() -> None:
    result = detect_sacred_polarity("")

    assert result["sacred_polarity_detected"] is False
    assert result["signals"] == []


def test_case_and_punctuation_do_not_prevent_detection() -> None:
    result = detect_sacred_polarity(
        "I value the balance of receptivity and action. "
        "I ONLY KNOW HOW TO DO, I DON'T KNOW HOW TO JUST BE!!!"
    )

    assert result["sacred_polarity_detected"] is True


def test_recommendation_warns_against_assigning_gender_when_framed() -> None:
    result = detect_sacred_polarity(
        "I value the balance of receptivity and action. "
        "I only know how to do, I don't know how to just be."
    )

    assert result["sacred_polarity_detected"] is True
    assert "gender" in cast(str, result["recommendation"]).lower()


def test_prior_user_polarity_framing_enables_later_signal() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I explicitly value the balance of receptivity and action.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is True


def test_latest_user_rejection_overrides_earlier_affirmative_framing() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I value the balance of receptivity and action.",
            },
            {
                "role": "user",
                "content": "I no longer relate to feminine and masculine energies.",
            },
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_later_affirmative_framing_restores_user_selected_lens() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I value the balance of receptivity and action.",
            },
            {
                "role": "user",
                "content": "I no longer relate to feminine and masculine energies.",
            },
            {
                "role": "user",
                "content": "I now find the balance of receptivity and action useful.",
            },
        ],
    )

    assert result["sacred_polarity_detected"] is True


def test_boundary_difficulty_without_current_or_prior_framing_stays_inactive() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [{"role": "user", "content": "Work has been stressful."}],
    )

    assert result["sacred_polarity_detected"] is False


def test_negated_prior_polarity_mention_does_not_enable_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I don't relate to feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_negated_conceptual_polarity_framing_does_not_enable_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I don't resonate with the concept of feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_negated_idea_framing_with_curly_apostrophe_does_not_enable_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I don\u2019t identify with the idea of feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_think_negation_does_not_enable_polarity_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I don't think feminine and masculine energies apply to me.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_qualified_think_negation_does_not_enable_polarity_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": (
                    "I don't think, given what I have experienced, feminine and "
                    "masculine energies apply to me."
                ),
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_affirmative_framing_after_qualified_rejection_enables_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": (
                    "I don't think, given what I have experienced, feminine and "
                    "masculine energies apply to me."
                ),
            },
            {
                "role": "user",
                "content": "I now find the balance of receptivity and action useful.",
            },
        ],
    )

    assert result["sacred_polarity_detected"] is True


def test_not_into_negation_does_not_enable_polarity_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I'm not into feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_no_longer_negation_does_not_enable_polarity_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I no longer believe in feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_rejection_verb_does_not_enable_polarity_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I reject the idea of feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_isnt_about_negation_does_not_enable_polarity_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "My experience isn't about feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_affirmative_frame_after_negated_mention_still_enables_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": "I don't relate to feminine and masculine energies, but I value feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is True


def test_quoted_prior_polarity_mention_does_not_enable_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": 'Someone mentioned "feminine and masculine energies".',
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_unquoted_framing_after_other_quotes_still_enables_detection() -> None:
    result = detect_sacred_polarity(
        "I can't set boundaries.",
        [
            {
                "role": "user",
                "content": 'Someone said "not this" and I value feminine and masculine energies "not that".',
            }
        ],
    )

    assert result["sacred_polarity_detected"] is True


def test_recommendation_present_when_not_detected() -> None:
    result = detect_sacred_polarity("I went to the gym today.")

    assert result["sacred_polarity_detected"] is False
    assert result["recommendation"]


def test_affirmative_frame_after_qualified_rejection_in_same_message_enables_detection() -> (
    None
):
    result = detect_sacred_polarity(
        "I don't think, given this, feminine and masculine energies apply to me, "
        "but I now find the balance of receptivity and action useful. "
        "I can't set boundaries."
    )

    assert result["sacred_polarity_detected"] is True


def test_rejected_polarity_frame_after_phrase_does_not_enable_detection() -> None:
    result = detect_sacred_polarity(
        "I only know how to do, I don't know how to just be.",
        [
            {
                "role": "user",
                "content": "Feminine and masculine energies don't apply to me.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_ascii_single_quoted_polarity_frame_does_not_enable_detection() -> None:
    result = detect_sacred_polarity(
        "I only know how to do, I don't know how to just be.",
        [
            {
                "role": "user",
                "content": "I'm repeating 'feminine and masculine energies'.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_contraction_apostrophe_does_not_hide_unquoted_polarity_frame() -> None:
    result = detect_sacred_polarity(
        "I only know how to do, I don't know how to just be.",
        [
            {
                "role": "user",
                "content": "I'm exploring feminine and masculine energies.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is True
