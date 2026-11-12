"""Tests for attribution-aware detector text normalization."""

from soulmap.runtime.io.text_normalization import mask_third_party_attribution


def test_quoted_third_party_speech_is_masked() -> None:
    masked = mask_third_party_attribution(
        'My friend said, "I am overwhelmed and my heart is racing."'
    )

    assert "overwhelmed" not in masked
    assert "heart is racing" not in masked


def test_unquoted_reported_speech_is_masked() -> None:
    masked = mask_third_party_attribution(
        "My friend told me I am overwhelmed and my heart is racing."
    )

    assert "overwhelmed" not in masked
    assert "heart is racing" not in masked


def test_users_own_statement_after_contrast_is_preserved() -> None:
    masked = mask_third_party_attribution(
        "My friend said I am overwhelmed, but my heart is racing too."
    )

    assert "overwhelmed" not in masked
    assert "my heart is racing too" in masked


def test_vietnamese_reported_speech_is_masked() -> None:
    masked = mask_third_party_attribution("Mẹ tôi nói tôi đang rất tức giận.")

    assert "rất tức giận" not in masked


def test_contractions_and_apostrophe_elisions_are_preserved() -> None:
    masked = mask_third_party_attribution(
        "'Cause I'm upset, my parents' support still matters."
    )

    assert "'cause i'm upset" in masked
    assert "parents' support" in masked


def test_unclosed_quote_masks_the_remaining_text() -> None:
    masked = mask_third_party_attribution('My friend wrote, "I cannot think straight')

    assert "cannot think straight" not in masked


def test_unattributed_quote_is_preserved_as_possible_user_language() -> None:
    masked = mask_third_party_attribution('"I am overwhelmed and my heart is racing."')

    assert "overwhelmed" in masked
    assert "heart is racing" in masked


def test_trailing_speech_attribution_masks_the_quote() -> None:
    masked = mask_third_party_attribution(
        '"I am overwhelmed and my heart is racing," my friend said.'
    )

    assert "overwhelmed" not in masked
    assert "heart is racing" not in masked


def test_unrelated_later_attribution_does_not_mask_user_quote() -> None:
    masked = mask_third_party_attribution(
        '"I am overwhelmed and my heart is racing." Later, my friend said hello.'
    )

    assert "overwhelmed" in masked
    assert "heart is racing" in masked


def test_hypothetical_third_party_speech_is_masked() -> None:
    masked = mask_third_party_attribution(
        "Hypothetically, my friend might say I am overwhelmed and my heart is racing."
    )

    assert "overwhelmed" not in masked
    assert "heart is racing" not in masked


def test_unquoted_speech_with_trailing_attribution_is_masked() -> None:
    masked = mask_third_party_attribution("I am overwhelmed, my friend said.")

    assert "overwhelmed" not in masked


def test_trailing_attribution_does_not_cross_a_sentence_boundary() -> None:
    masked = mask_third_party_attribution("I am overwhelmed. My friend said hello.")

    assert "overwhelmed" in masked


def test_trailing_reporter_with_complement_does_not_mask_users_clause() -> None:
    masked = mask_third_party_attribution(
        "I am overwhelmed, my friend said she was upset."
    )

    assert "overwhelmed" in masked
    assert "she was upset" not in masked


def test_possessive_section_labels_are_not_treated_as_attribution() -> None:
    for message in (
        "My situation: I feel completely lost.",
        "My dilemma: Part of me wants to leave.",
    ):
        assert mask_third_party_attribution(message) == message.lower()


def test_possessive_person_labels_still_mask_attributed_speech() -> None:
    masked = mask_third_party_attribution(
        "My sister: I feel completely lost and do not know what I want."
    )

    assert "completely lost" not in masked


def test_reported_speech_keeps_following_first_person_clause_attributed() -> None:
    masked = mask_third_party_attribution(
        "My friend said I've lost my voice, I don't know what I want to say."
    )

    assert "lost my voice" not in masked
    assert "don't know what i want to say" not in masked


def test_user_statement_after_explicit_contrast_is_preserved() -> None:
    masked = mask_third_party_attribution(
        "My friend said I am overwhelmed, but I feel overwhelmed too."
    )

    assert "overwhelmed" not in masked.split("but", maxsplit=1)[0]
    assert "but i feel overwhelmed too" in masked


def test_attributed_thoughts_and_beliefs_are_masked() -> None:
    masked = mask_third_party_attribution(
        "My friend thinks I feel spiritually empty and disconnected from everything."
    )

    assert "feel spiritually empty" not in masked
    assert "disconnected from everything" not in masked


def test_vietnamese_attributed_thought_is_masked() -> None:
    masked = mask_third_party_attribution(
        "Mẹ tôi nghĩ rằng tôi cảm thấy trống rỗng và mất kết nối."
    )

    assert "cảm thấy trống rỗng" not in masked
    assert "mất kết nối" not in masked


def test_multiple_speakers_with_cognitive_attribution_are_masked() -> None:
    masked = mask_third_party_attribution(
        "My friend said I feel spiritually empty. "
        "My sister believes I have lost my faith."
    )

    assert "spiritually empty" not in masked
    assert "lost my faith" not in masked


def test_user_authored_statement_after_cognitive_attribution_is_preserved() -> None:
    masked = mask_third_party_attribution(
        "My friend thinks I feel spiritually empty, but I feel spiritually empty too."
    )

    assert "spiritually empty" not in masked.split("but", maxsplit=1)[0]
    assert "but i feel spiritually empty too" in masked
