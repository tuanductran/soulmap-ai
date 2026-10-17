"""Edge-case coverage for the AI-dependency detector.

Signal phrases are authored in the canonical Markdown runtime source
skills/safety/dependency-detection.md and exercised here as behavioral
regression cases.
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
    """A repeated signal must be recorded only once.

    The detector guards each append on the signal not already being present.
    """
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
    """A lone decision-seeking phrase must land on moderate, not high.

    It adds a single point, which reaches the moderate threshold exactly
    without crossing into high dependency.
    """
    result = analyze_dependency([_user("Should I do this or not?")])

    assert result["level"] == "MODERATE_DEPENDENCY"


def test_each_unexcluded_decision_seeking_occurrence_is_counted() -> None:
    result = analyze_dependency([_user("Should I leave? Should I stay?")])

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert result["signals"] == ["decision_seeking_count: 2"]


def test_nested_decision_seeking_phrase_is_counted_once() -> None:
    result = analyze_dependency([_user("What should I do?")])

    assert result["level"] == "MODERATE_DEPENDENCY"
    assert result["score"] == 1
    assert result["signals"] == ["decision_seeking_count: 1"]


def test_recommendation_present_for_each_level() -> None:
    low = analyze_dependency([_user("Had a quiet day.")])
    moderate = analyze_dependency([_user("Should I do this or not?")])
    high = analyze_dependency(
        [_user("You are all I have."), _user("I have no one else.")]
    )

    assert low["recommendation"]
    assert moderate["recommendation"]
    assert high["recommendation"]


def test_quoted_dependency_signal_is_not_treated_as_user_endorsement() -> None:
    result = analyze_dependency(
        [_user('My friend said, "you are all I have"; how should I respond?')]
    )

    assert result["level"] == "MODERATE_DEPENDENCY"
    assert result["score"] == 1
    assert not any("dependency_keyword" in signal for signal in result["signals"])


def test_third_party_dependency_signal_is_not_treated_as_user_endorsement() -> None:
    result = analyze_dependency(
        [_user("My coworker told his chatbot you're the only one who understands me.")]
    )

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["score"] == 0
    assert result["signals"] == []


def test_comma_does_not_end_third_party_attribution_scope() -> None:
    result = analyze_dependency([_user("My friend said, you are all I have.")])

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["score"] == 0
    assert result["signals"] == []


def test_first_person_restart_after_comma_ends_third_party_scope() -> None:
    result = analyze_dependency(
        [_user("My friend said hi, I feel you are all I have.")]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert any("dependency_keyword" in signal for signal in result["signals"])


def test_quoted_compound_boundary_does_not_end_hypothetical_scope() -> None:
    result = analyze_dependency(
        [_user('Hypothetically, the phrase ", I" is followed by you are all I have.')]
    )

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["score"] == 0
    assert result["signals"] == []



def test_hypothetical_dependency_signal_is_not_treated_as_endorsement() -> None:
    result = analyze_dependency(
        [_user("If I ever said you are all I have, that would be a fictional example.")]
    )

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["score"] == 0
    assert result["signals"] == []


def test_explicit_negation_does_not_count_as_dependency_endorsement() -> None:
    result = analyze_dependency(
        [_user("I don't feel that you are the only one who understands me.")]
    )

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["score"] == 0
    assert result["signals"] == []


def test_first_person_dependency_signal_still_reaches_high_dependency() -> None:
    result = analyze_dependency(
        [_user("I feel like you are all I have, and I have no one else.")]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert any("dependency_keyword" in signal for signal in result["signals"])


def test_first_person_signal_after_negated_clause_is_preserved() -> None:
    result = analyze_dependency(
        [_user("I never said you are my only support, I feel you are all I have.")]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2


def test_first_person_signal_after_quoted_third_party_clause_is_preserved() -> None:
    result = analyze_dependency(
        [_user('My friend said "you are all I have," I feel you are all I have.')]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2


def test_third_party_cue_does_not_hide_a_later_first_person_signal() -> None:
    result = analyze_dependency(
        [
            _user(
                "My coworker told his chatbot you're the only one who understands me, "
                "but I feel you are all I have."
            )
        ]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2


def test_first_person_signal_after_period_is_preserved() -> None:
    result = analyze_dependency(
        [_user("My friend said you are all I have. I feel you are all I have.")]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert any("dependency_keyword" in signal for signal in result["signals"])


def test_quoted_context_cue_does_not_suppress_real_dependency_signal() -> None:
    result = analyze_dependency(
        [_user('The word "hypothetically" explains why you are all I have.')]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert any("dependency_keyword" in signal for signal in result["signals"])


def test_contractions_do_not_open_unintended_quoted_spans() -> None:
    result = analyze_dependency(
        [_user("I'm worried because you're the only one who understands me.")]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert any("dependency_keyword" in signal for signal in result["signals"])


def test_decision_seeking_occurrence_in_hypothetical_context_is_excluded() -> None:
    result = analyze_dependency(
        [_user("Hypothetically, what would you do; but seriously, help me decide.")]
    )

    assert result["level"] == "MODERATE_DEPENDENCY"
    assert result["score"] == 1
    assert result["signals"] == ["decision_seeking_count: 1"]


def test_hypothetical_cue_does_not_hide_a_later_first_person_signal() -> None:
    result = analyze_dependency(
        [
            _user(
                "If I ever said you are all I have, but I mean it now: "
                "I have no one else."
            )
        ]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2


def test_current_message_is_counted_when_text_repeats_last_user_turn() -> None:
    message = "Help me decide."
    history = [_user(message)]

    result = analyze_dependency(history, current_message=message)

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert result["signals"] == ["decision_seeking_count: 2"]


def test_current_message_is_counted_after_trailing_assistant_turn() -> None:
    message = "Help me decide."
    history = [_user(message), {"role": "assistant", "content": "I hear you."}]

    result = analyze_dependency(history, current_message=message)

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert result["signals"] == ["decision_seeking_count: 2"]


def test_unrelated_quote_does_not_end_hypothetical_scope() -> None:
    result = analyze_dependency(
        [
            _user(
                'Hypothetically, the phrase "hello" could be followed by '
                "you are all I have in a fictional example."
            )
        ]
    )

    assert result["level"] == "LOW_DEPENDENCY"
    assert result["score"] == 0
    assert result["signals"] == []


def test_unrelated_quote_ends_third_party_attribution_scope() -> None:
    result = analyze_dependency(
        [_user('My friend said the phrase "hello" and then said you are all I have.')]
    )

    assert result["level"] == "HIGH_DEPENDENCY"
    assert result["score"] == 2
    assert any("dependency_keyword" in signal for signal in result["signals"])
