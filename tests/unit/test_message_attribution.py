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
    masked = mask_third_party_attribution(
        "Mẹ tôi nói tôi đang rất tức giận."
    )

    assert "rất tức giận" not in masked


def test_contractions_and_apostrophe_elisions_are_preserved() -> None:
    masked = mask_third_party_attribution(
        "'Cause I'm upset, my parents' support still matters."
    )

    assert "'cause i'm upset" in masked
    assert "parents' support" in masked


def test_unclosed_quote_masks_the_remaining_text() -> None:
    masked = mask_third_party_attribution(
        'My friend wrote, "I cannot think straight'
    )

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
