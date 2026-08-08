"""Edge-case coverage for the AI-dependency detector.

Phrases used below are taken verbatim from
soulmap.runtime.config.safety (DEPENDENCY_KEYWORDS, DECISION_SEEKING,
ISOLATION_SIGNALS), the static config module this detector imports from
directly. Nothing here is guessed.
"""

from soulmap.runtime.detectors.dependency_detector import analyze_dependency


def _user(content: str) -> dict[str, str]:
    return {"role": "user", "content": content}


def test_no_user_messages_returns_no_data() -> None:
    result = analyze_dependency([])

    assert result["level"] == "NO_DATA"
    assert result["score"] == 0


def test_non_user_only_messages_return_no_data() -> None:
    result = analyze_dependency([{"role": "assistant", "content": "How can I help?"}])

    assert result["level"] == "NO_DATA"


def test_low_dependency_for_ordinary_message() -> None:
    result = analyze_dependency([_user("I had a good day today, thanks for asking.")])

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["signals"] == []


def test_single_dependency_keyword_reaches_high_dependency() -> None:
    result = analyze_dependency([_user("I don't know what I would do without you.")])

    assert result["level"] == "HIGH_DEPENDENCY"
    assert any("dependency_keyword" in s for s in result["signals"])


def test_two_dependency_keywords_across_messages_reach_high_dependency() -> None:
    result = analyze_dependency(
        [
            _user("You are all I have right now."),
            _user("I have no one else to talk to."),
        ]
    )

    assert result["level"] == "HIGH_DEPENDENCY"


def test_dependency_regex_pattern_is_detected() -> None:
    result = analyze_dependency([_user("Only you truly understand me.")])

    assert result["level"] == "HIGH_DEPENDENCY"
    assert any("dependency_pattern" in s for s in result["signals"])


def test_duplicate_keyword_across_messages_is_not_double_counted() -> None:
    """The same signal string should only be added to signals_found once,
    per the `if signal not in signals_found` guard."""
    result = analyze_dependency(
        [
            _user("You are all I have."),
            _user("Really, you are all I have."),
        ]
    )

    keyword_signals = [s for s in result["signals"] if "you are all i have" in s]
    assert len(keyword_signals) == 1


def test_decision_seeking_phrases_are_counted() -> None:
    result = analyze_dependency(
        [_user("What should I do here? Tell me if this is the right choice.")]
    )

    assert any("decision_seeking_count" in s for s in result["signals"])


def test_isolation_signal_is_detected() -> None:
    result = analyze_dependency([_user("I prefer talking to you over real people.")])

    assert result["level"] == "HIGH_DEPENDENCY"
    assert any("isolation_signal" in s for s in result["signals"])


def test_high_message_volume_adds_a_signal() -> None:
    messages = [_user(f"Just checking in, message number {i}.") for i in range(11)]
    result = analyze_dependency(messages)

    assert any("high_message_volume" in s for s in result["signals"])


def test_single_decision_seeking_phrase_reaches_moderate_dependency() -> None:
    """A lone decision-seeking phrase adds only +1, landing exactly on the
    MODERATE_DEPENDENCY threshold (1) without crossing into HIGH (2)."""
    result = analyze_dependency([_user("Should I do this or not?")])

    assert result["level"] == "MODERATE_DEPENDENCY"


def test_recommendation_present_for_each_level() -> None:
    low = analyze_dependency([_user("Had a quiet day.")])
    moderate = analyze_dependency([_user("Should I do this or not?")])
    high = analyze_dependency(
        [_user("You are all I have."), _user("I have no one else.")]
    )

    assert low["recommendation"]
    assert moderate["recommendation"]
    assert high["recommendation"]
