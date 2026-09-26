from __future__ import annotations

from soulmap.runtime.knowledge.stage_classifier import (
    load_stage_classifier,
    parse_stage_classifier,
)
from soulmap.runtime.routing.stage_detector import detect_stage


def _user(content: str) -> dict[str, str]:
    return {"role": "user", "content": content}


def test_stage_classifier_loads_the_shipped_contract() -> None:
    rules = load_stage_classifier()

    assert len(rules.stages) == 6
    assert rules.thresholds == {1: 0, 2: 4, 3: 6, 4: 8, 5: 10, 6: 12}
    assert rules.recency_multipliers == (0.5, 1.0, 1.5, 2.0, 3.0)


def test_stage_classifier_rejects_missing_stage() -> None:
    rules = load_stage_classifier()
    source = "\n".join(
        f"### Stage {stage.number}, {stage.name.lower()}" for stage in rules.stages[:-1]
    )

    try:
        parse_stage_classifier(source)
    except ValueError as error:
        assert "Expected 6 stage definitions" in str(error)
    else:
        raise AssertionError("Incomplete stage classifier should be rejected")


def test_stage_defaults_to_arrival_without_user_history() -> None:
    result = detect_stage([{"role": "assistant", "content": "How are you?"}])

    assert result["stage"] == 1
    assert result["confidence"] == "DEFAULT"
    assert result["signals"] == []


def test_first_session_stays_at_stage_one() -> None:
    result = detect_stage([_user("I trust myself and I know what I need.")])

    assert result["stage"] == 1
    assert result["confidence"] == "LOW"


def test_current_turn_uses_the_three_x_recency_multiplier() -> None:
    result = detect_stage(
        [
            _user("This feels quiet now."),
            _user("Maybe I can be honest about this."),
        ]
    )

    assert result["stage"] == 2
    assert result["score"] == 6.0
    assert result["signals"] == ["maybe i"]


def test_recent_five_messages_are_the_only_messages_scored() -> None:
    history = [_user("Maybe I can be honest about this.")] * 3
    history.extend(
        [
            _user("Nothing useful here."),
            _user("Still nothing."),
            _user("Maybe I can be honest about this."),
        ]
    )
    result = detect_stage(history)

    assert result["stage"] == 2
    assert result["signals"] == ["maybe i"]


def test_threshold_prevents_single_stage_three_signal_from_classifying() -> None:
    result = detect_stage(
        [
            _user("This is neutral."),
            _user("I see a connection."),
        ]
    )

    assert result["stage"] == 1


def test_close_scores_choose_the_lower_stage() -> None:
    result = detect_stage(
        [
            _user("I see a connection."),
            _user("Maybe I can be honest about this."),
        ]
    )

    assert result["stage"] == 2


def test_memory_can_raise_the_minimum_stage() -> None:
    result = detect_stage(
        [
            _user("I trust myself."),
            _user("I know what I need."),
        ],
        {"session_count": 10},
    )

    assert result["stage"] >= 2


def test_prior_stage_prevents_unjustified_regression() -> None:
    result = detect_stage(
        [
            _user("I don't know what to do."),
            _user("I feel lost."),
        ],
        {"prior_stage": 4},
    )

    assert result["stage"] == 4


def test_destabilization_allows_stage_regression() -> None:
    result = detect_stage(
        [
            _user("I don't know what to do."),
            _user("I feel lost."),
        ],
        {"prior_stage": 4, "destabilization_signals": ["acute distress"]},
    )

    assert result["stage"] == 1
