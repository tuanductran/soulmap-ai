from __future__ import annotations

from typing import cast

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


def test_should_synthesize_covers_explicit_natural_threshold_and_no_trigger() -> None:
    short_history = _user_messages(["one", "two"])
    reflective_history = _user_messages([f"message {index}" for index in range(10)])
    long_history = _user_messages([f"message {index}" for index in range(12)])

    assert synthesizer.should_synthesize("Can you synthesize this?", short_history) == {
        "should": True,
        "reason": "explicit_request",
    }
    assert synthesizer.should_synthesize(
        "I wonder why this repeats.", reflective_history
    ) == {
        "should": True,
        "reason": "natural_pause_long_session",
    }
    assert synthesizer.should_synthesize("I am still here.", long_history) == {
        "should": True,
        "reason": "long_session_threshold",
    }
    assert synthesizer.should_synthesize("I am still here.", short_history) == {
        "should": False,
        "reason": "not_triggered",
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
