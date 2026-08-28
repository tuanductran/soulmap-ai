"""Edge-case coverage for the recurring-pattern detector.

Phrases used below are taken verbatim from
skills/frameworks/pattern-mapper.md ("Pattern 1: Abandonment Loop",
"Pattern 2: Approval Seeking" - Detection signals and Cycle phrases
sections), which this detector loads from via
soulmap.runtime.knowledge.pattern_source. Nothing here is guessed.
"""

from typing import cast

from soulmap.runtime.detectors.pattern_detector import detect_patterns


def _user(content: str) -> dict[str, str]:
    return {"role": "user", "content": content}


def test_single_user_message_waits_for_more_and_names_nothing() -> None:
    result = detect_patterns([_user("They always leave eventually.")])

    assert result["wait_for_more"] is True
    assert result["patterns_detected"] == []
    assert result["primary_pattern"] is None


def test_no_user_messages_also_waits_for_more() -> None:
    result = detect_patterns([{"role": "assistant", "content": "Hi there."}])

    assert result["wait_for_more"] is True


def test_single_keyword_across_two_messages_is_detected() -> None:
    result = detect_patterns(
        [_user("People always leave."), _user("I don't know why they always leave.")]
    )

    assert result["wait_for_more"] is False
    patterns = cast(list[dict[str, object]], result["patterns_detected"])
    assert any(p["pattern"] for p in patterns)
    assert result["primary_pattern"] is not None


def test_cycle_phrase_scores_higher_than_a_single_keyword() -> None:
    """A cycle phrase alone crosses the detection threshold.

    Cycle phrases score three against two for a plain keyword, so one is
    enough on its own.
    """
    result = detect_patterns(
        [_user("It always ends the same."), _user("Every relationship is the same.")]
    )

    assert result["wait_for_more"] is False
    assert result["primary_pattern"] is not None


def test_no_pattern_signals_is_not_detected() -> None:
    result = detect_patterns(
        [_user("I had lunch with a friend."), _user("We talked about a movie.")]
    )

    assert result["patterns_detected"] == []
    assert result["primary_pattern"] is None
    assert result["combination"] is False
    assert "no strong pattern" in cast(str, result["recommendation"]).lower()


def test_two_distinct_patterns_are_reported_as_combination() -> None:
    result = detect_patterns(
        [
            _user("People always leave, they always leave eventually."),
            _user("I always worry about what they think, always checking."),
        ]
    )

    patterns = cast(list[dict[str, object]], result["patterns_detected"])
    assert len(patterns) >= 2
    assert result["combination"] is True
    assert "combination detected" in cast(str, result["recommendation"]).lower()


def test_single_pattern_recommendation_names_the_pattern() -> None:
    result = detect_patterns(
        [_user("People always leave."), _user("They always leave eventually.")]
    )

    assert result["combination"] is False
    patterns = cast(list[dict[str, object]], result["patterns_detected"])
    primary_name = patterns[0]["name"]
    assert cast(str, primary_name) in cast(str, result["recommendation"])


def test_detected_pattern_entry_has_expected_shape() -> None:
    result = detect_patterns(
        [_user("People always leave."), _user("They always leave eventually.")]
    )

    patterns = cast(list[dict[str, object]], result["patterns_detected"])
    entry = patterns[0]
    assert set(entry) >= {
        "pattern",
        "name",
        "score",
        "signals",
        "reflection_en",
        "soulmap_role",
    }
    assert isinstance(entry["score"], int)
    assert entry["score"] >= 2
