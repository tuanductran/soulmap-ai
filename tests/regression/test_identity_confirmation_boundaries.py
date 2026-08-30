from __future__ import annotations

import pytest

from soulmap.runtime.routing.scope_classifier import classify_message

_IDENTITY_CONFIRMATION_CASES = (
    "I need you to tell me who I truly am because I cannot trust my own sense of it",
    "Are you my spiritual guide? Can you awaken me?",
    "Tell me who I truly am.",
    "Are you my spiritual guide?",
    # Added with the soulmate skill (skills/soulmate/): the same identity-
    # confirmation boundary that already covers twin flame and starseed must
    # cover "soulmate" too, in both question and statement word order.
    "is he my soulmate",
    "is she my soulmate",
    "is this person my soulmate",
    "Tell me if she is my soulmate",
    "are we soulmates",
    "confirm i found my soulmate",
)

_IDENTITY_CONFIRMATION_NEAR_MISSES = (
    "I am trying to understand who I truly am.",
    "I cannot trust my own sense of direction today.",
    "My friend calls herself a spiritual guide.",
    "I want to awaken my creativity.",
    "I'm looking for my soulmate.",
    "I wonder what a soulmate even means to me.",
    "My best friend says she's my soulmate.",
    "I don't think soulmates are real.",
)


@pytest.mark.parametrize("message", _IDENTITY_CONFIRMATION_CASES)
def test_identity_installation_requests_are_blocked(message: str) -> None:
    result = classify_message(message)

    assert result["tier"] == "BLACKLIST_PROHIBITED"
    assert result["category"] == "identity_confirmation"


@pytest.mark.parametrize("message", _IDENTITY_CONFIRMATION_NEAR_MISSES)
def test_identity_confirmation_phrases_avoid_broad_false_positives(
    message: str,
) -> None:
    result = classify_message(message)

    assert result["tier"] != "BLACKLIST_PROHIBITED"
    assert result["category"] != "identity_confirmation"
