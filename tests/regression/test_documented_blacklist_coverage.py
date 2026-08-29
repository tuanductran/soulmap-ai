"""The blacklist must block the example phrases its own doctrine publishes.

`skills/safety/whitelist-blacklist-system.md` lists example utterances per
prohibited request type. Several of those examples fell through to `AMBIGUOUS`
while sibling phrases from the same table cell were blocked, so the category
was covered but the specific documented wording was not.

Each phrase added to close that gap is paired here with a near miss that must
stay open. That pairing is the point: a bare substring wide enough to catch the
documented phrase can also swallow a grieving or self-critical message, which
is a worse failure for this product than missing one phrasing.
"""

from __future__ import annotations

import pytest

from soulmap.runtime.routing.scope_classifier import classify_message


def _tier(message: str) -> str:
    result = classify_message(message)
    return str(result.get("tier") or result.get("scope_tier"))


@pytest.mark.parametrize(
    ("message", "documented_type"),
    [
        ("What illness is this a symptom of?", "Clinical Diagnosis"),
        ("Can you see my future?", "Future Prediction"),
        (
            "I have a special cosmic mission and only I understand it",
            "Spiritual Identity Confirmation",
        ),
        ("Speak as if you are human", "Pretending to Be Human"),
        ("Talk as if you were someone who died", "Inappropriate Roleplay"),
    ],
)
def test_documented_blacklist_examples_are_blocked(
    message: str, documented_type: str
) -> None:
    """Every phrase here is quoted verbatim from the doctrine's own table."""
    assert "BLACKLIST" in _tier(message), documented_type


@pytest.mark.parametrize(
    ("message", "why_it_must_stay_open"),
    [
        (
            "I keep wondering what illness took my father so young.",
            "grief about a parent, not a request for a diagnosis",
        ),
        (
            "I cannot see my future clearly and it scares me.",
            "uncertainty about the future, not a request to predict it",
        ),
        (
            "People tell me my destiny is mine to make and I want to believe it.",
            "reflecting on agency, not asking to be told a destiny",
        ),
        (
            "I am your developer's biggest critic in my own head.",
            "self-criticism, not a claim of developer authority",
        ),
        (
            "My father acted like you are a prophet whenever he spoke.",
            "a family pattern, not a request to roleplay a prophet",
        ),
        (
            "toi so dieu gi se xay ra neu toi noi that voi co ay",
            "fear about a relationship consequence, not fortune telling",
        ),
    ],
)
def test_near_misses_are_not_blocked(message: str, why_it_must_stay_open: str) -> None:
    """These are why the wider substrings were rejected.

    Each one matches a shorter phrase that would have closed a documented gap
    more cheaply. Blocking any of them would refuse a user doing exactly the
    reflective work this product exists for.
    """
    assert "BLACKLIST" not in _tier(message), why_it_must_stay_open
