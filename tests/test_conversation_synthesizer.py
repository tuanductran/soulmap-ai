from __future__ import annotations

from dataclasses import replace
from typing import cast

import pytest

from soulmap.runtime.knowledge.runtime_config import DETECTOR_CONFIG
from soulmap.runtime.knowledge.synthesis_source import load_synthesis_rules
from soulmap.runtime.synthesis import conversation_synthesizer as synthesizer


def _user_messages(contents: list[str]) -> list[dict[str, str]]:
    return [{"role": "user", "content": content} for content in contents]


def test_extract_themes_scores_recurring_domains_and_keeps_user_anchors() -> None:
    messages = [
        {"role": "assistant", "content": "What feels present?"},
        {
            "role": "user",
            "content": "I feel alone and want connection, but I keep pushing people away. My choice matters.",
        },
        {
            "role": "user",
            "content": "I am lonely again. I want connection, then I pull back. I need my own path.",
        },
    ]

    themes = synthesizer.extract_themes(messages)

    assert themes.get("emotional") == [
        {"theme": "loneliness", "score": 2, "anchors": [1, 2]}
    ]
    assert themes.get("values") == [
        {"theme": "autonomy", "score": 2, "anchors": [1, 2]}
    ]
    assert themes.get("conflicts") == [
        {"theme": "closeness_vs_distance", "score": 2, "anchors": [1, 2]}
    ]


def test_extract_themes_ignores_non_user_messages_and_limits_anchor_count() -> None:
    messages = [
        {"role": "assistant", "content": "You are not alone."},
        {"role": "user", "content": "I feel alone."},
        {"role": "user", "content": "I feel lonely."},
        {"role": "user", "content": "I am isolated."},
    ]

    themes = synthesizer.extract_themes(messages)

    assert themes.get("emotional") == [
        {"theme": "loneliness", "score": 3, "anchors": [1, 2]}
    ]
    assert themes.get("values") == []
    assert themes.get("conflicts") == []


def test_merge_memory_themes_requires_matching_current_themes() -> None:
    extracted = cast(
        synthesizer.ExtractedThemes,
        {
            "emotional": [{"theme": "loneliness", "score": 2, "anchors": [0, 1]}],
            "values": [{"theme": "autonomy", "score": 2, "anchors": [0, 1]}],
            "conflicts": [],
        },
    )

    merged = synthesizer.merge_memory_themes(
        extracted,
        {
            "recurring_themes": ["loneliness", "autonomy", "not-a-current-theme", 3],
            "session_count": 4,
        },
    )

    assert merged.get("longitudinal") == ["loneliness", "autonomy"]
    assert merged.get("session_count") == 4


def test_merge_memory_themes_handles_invalid_or_empty_memory_values() -> None:
    extracted = cast(
        synthesizer.ExtractedThemes,
        {"emotional": [], "values": [], "conflicts": []},
    )

    assert (
        synthesizer.merge_memory_themes(extracted, {"recurring_themes": "loneliness"})
        == extracted
    )
    assert (
        synthesizer.merge_memory_themes(extracted, {"recurring_themes": []})
        == extracted
    )


def test_synthesis_rules_combine_python_config_and_semantic_markdown() -> None:
    rules = load_synthesis_rules()

    assert rules.minimum_user_messages == 6
    assert rules.automatic_user_messages == 10
    assert rules.minimum_recurring_themes == 2
    assert rules.max_themes == 3
    assert rules.max_anchors == 2
    assert rules.max_longitudinal == 3
    assert rules.minimum_theme_occurrences == 2
    assert rules.minimum_sessions_for_longitudinal == 3
    assert rules.max_memory_themes == 5
    assert "can you synthesize" in rules.explicit_requests
    assert "session_opening" in rules.response_guidance
    assert "recommendation" in rules.response_guidance


def test_should_synthesize_requires_two_distinct_recurring_themes() -> None:
    one_theme = _user_messages(
        [f"I feel lonely in message {index}." for index in range(9)]
    )
    two_themes = _user_messages(
        [
            f"I feel lonely and my own path matters in message {index}."
            for index in range(9)
        ]
    )

    assert synthesizer.should_synthesize("I am still here.", one_theme) == {
        "should": False,
        "reason": "not_triggered",
    }
    assert synthesizer.should_synthesize(
        "I feel lonely and my own path matters too.", two_themes
    ) == {
        "should": True,
        "reason": "recurring_themes_long_session",
    }


def test_should_synthesize_counts_current_user_message() -> None:
    history = _user_messages(
        [
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
            "I feel lonely and my own path matters.",
        ]
    )

    assert synthesizer.should_synthesize(
        "I feel lonely and my own path matters.", history
    ) == {
        "should": True,
        "reason": "recurring_themes_long_session",
    }


def test_should_synthesize_explicit_request_is_independent_of_session_length() -> None:
    assert synthesizer.should_synthesize(
        "Can you synthesize this?", _user_messages(["one", "two"])
    ) == {
        "should": True,
        "reason": "explicit_request",
    }


def test_synthesize_returns_insufficient_data_and_theme_outcomes() -> None:
    insufficient_data = synthesizer.synthesize("pattern?", _user_messages(["one"] * 4))
    insufficient_themes = synthesizer.synthesize(
        "pattern?", _user_messages(["plain"] * 6)
    )

    assert insufficient_data["synthesis_ready"] is False
    assert insufficient_data["reason"] == "insufficient_data"
    assert insufficient_themes["synthesis_ready"] is False
    assert insufficient_themes["reason"] == "insufficient_recurring_themes"


def test_synthesize_includes_current_message_with_prior_history() -> None:
    history = _user_messages(
        [
            "I feel lonely.",
            "My own path matters.",
            "I am thinking it through.",
            "I am taking it slowly.",
            "I want to stay with this.",
        ]
    )

    result = synthesizer.synthesize(
        "I feel isolated, and I need my own path.",
        history,
    )

    assert result["synthesis_ready"] is True
    themes = cast(dict[str, object], result["themes"])
    assert themes["emotional"] == [
        {"theme": "loneliness", "score": 2, "anchors": [0, 5]}
    ]
    assert themes["values"] == [{"theme": "autonomy", "score": 2, "anchors": [1, 5]}]


def test_synthesize_allows_explicit_request_with_short_longitudinal_history() -> None:
    history = _user_messages(
        [
            "I feel lonely and my own path matters.",
        ]
    )
    result = synthesizer.synthesize(
        "Can you synthesize what keeps returning? I feel lonely and my own path matters.",
        history,
        {"recurring_themes": ["loneliness", "autonomy"], "session_count": 4},
    )

    assert result["synthesis_ready"] is True
    assert result["is_longitudinal"] is True
    assert len(cast(list[object], result["top_themes"])) >= 1


def test_synthesize_returns_grounded_longitudinal_theme_frame() -> None:
    history = _user_messages(
        [
            "I feel alone and my choice matters. I want connection but push away.",
            "I feel lonely and need my own path. I want connection and pull back.",
            "I am isolated. My choice matters. I want connection but push away.",
            "I feel alone again and need my own path. I want connection then pull back.",
            "I am lonely and want connection but push away. My choice matters.",
            "I feel isolated and want connection, but I pull back. My own path matters.",
        ]
    )

    result = synthesizer.synthesize(
        "Can you reflect back what is recurring?",
        history,
        {
            "recurring_themes": ["loneliness", "autonomy", "unrelated"],
            "session_count": 3,
        },
    )

    assert result["synthesis_ready"] is True
    assert result["is_longitudinal"] is True
    themes = cast(dict[str, object], result["themes"])
    assert themes["longitudinal"] == ["loneliness", "autonomy"]
    assert len(cast(list[object], result["top_themes"])) == 3
    assert "These threads are yours" in str(result["synthesis_frame"])
    assert "Of these, which one feels most alive tonight?" in str(
        result["synthesis_frame"]
    )
    assert "Longitudinal data available." in str(result["recommendation"])
    guidance = load_synthesis_rules().response_guidance
    assert guidance["value_theme_suffix"].startswith("-")
    assert guidance["conflict_theme_suffix"].startswith("-")


def test_synthesize_uses_current_session_opening_without_longitudinal_memory() -> None:
    history = _user_messages(
        [
            "I feel alone and my choice matters. I want connection but push away.",
            "I feel lonely and need my own path. I want connection and pull back.",
            "I am isolated. My choice matters. I want connection but push away.",
            "I feel alone again and need my own path. I want connection then pull back.",
            "I am lonely and want connection but push away. My choice matters.",
            "I feel isolated and want connection, but I pull back. My own path matters.",
        ]
    )

    result = synthesizer.synthesize("Can you reflect back what is recurring?", history)

    assert result["synthesis_ready"] is True
    assert result["is_longitudinal"] is False
    assert str(result["synthesis_frame"]).startswith("Across what you've shared today")


def test_synthesis_response_policy_is_markdown_authored() -> None:
    history = _user_messages(
        [
            "I feel alone and my choice matters. I want connection but push away.",
            "I feel lonely and need my own path. I want connection and pull back.",
            "I am isolated. My choice matters. I want connection but push away.",
            "I feel alone again and need my own path. I want connection then pull back.",
            "I am lonely and want connection but push away. My choice matters.",
            "I feel isolated and want connection, but I pull back. My own path matters.",
        ]
    )

    result = synthesizer.synthesize("Can you reflect back what is recurring?", history)
    assert result["synthesis_ready"] is True
    assert "These threads are yours" in str(result["synthesis_frame"])
    assert "Activate Conversation Pattern Synthesizer" in str(result["recommendation"])


def test_value_and_conflict_thresholds_use_runtime_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rules = load_synthesis_rules()
    monkeypatch.setattr(
        synthesizer, "_rules", lambda: replace(rules, minimum_theme_occurrences=3)
    )
    messages = _user_messages(
        [
            "I feel lonely and my own path matters. I want connection but pull away.",
            "I feel lonely and my own path matters. I want connection but pull away.",
        ]
    )

    themes = synthesizer.extract_themes(messages)

    assert themes.get("emotional", []) == []
    assert themes.get("values", []) == []
    assert themes.get("conflicts", []) == []


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "zero", "negative", "boolean", "non_integer"],
)
def test_synthesis_loader_rejects_invalid_python_limits(
    monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    """Reject incomplete or invalid Python-owned synthesis limits."""
    values = dict(DETECTOR_CONFIG["conversation_synthesis"])
    if mutation == "missing":
        values.pop("max_themes")
    elif mutation == "extra":
        values["unexpected"] = 1
    elif mutation == "zero":
        values["max_themes"] = 0
    elif mutation == "negative":
        values["max_themes"] = -1
    elif mutation == "boolean":
        values["max_themes"] = cast(int, True)
    else:
        values["max_themes"] = cast(int, "3")

    load_synthesis_rules.cache_clear()
    monkeypatch.setitem(DETECTOR_CONFIG, "conversation_synthesis", values)
    try:
        with pytest.raises(ValueError, match="Conversation synthesis limits"):
            load_synthesis_rules()
    finally:
        load_synthesis_rules.cache_clear()
