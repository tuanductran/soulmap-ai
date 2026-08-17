from __future__ import annotations

import pytest

from soulmap.runtime.routing.scope_classifier import classify_message

_IDENTITY_CONFIRMATION_CASES = (
    "I need you to tell me who I truly am because I cannot trust my own sense of it",
    "Are you my spiritual guide? Can you awaken me?",
    "Tell me who I truly am.",
    "Are you my spiritual guide?",
)

_IDENTITY_CONFIRMATION_NEAR_MISSES = (
    "I am trying to understand who I truly am.",
    "I cannot trust my own sense of direction today.",
    "My friend calls herself a spiritual guide.",
    "I want to awaken my creativity.",
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
