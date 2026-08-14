from __future__ import annotations

from soulmap.runtime.routing.stage_detector import detect_stage


def _user(content: str) -> dict[str, str]:
    return {"role": "user", "content": content}


def test_stage_defaults_to_arrival_when_history_has_no_user_message() -> None:
    result = detect_stage([{"role": "assistant", "content": "How are you?"}])

    assert result["stage"] == 1
    assert result["confidence"] == "DEFAULT"
    assert result["signals"] == []


def test_stage_uses_low_confidence_when_user_message_has_no_stage_signal() -> None:
    result = detect_stage([_user("I went for a quiet walk this morning.")])

    assert result["stage"] == 1
    assert result["confidence"] == "LOW"
    assert result["score"] == 0


def test_stage_uses_low_confidence_for_old_single_signal() -> None:
    result = detect_stage(
        [
            _user("Maybe I can be honest about this."),
            _user("I am listening to myself today."),
            _user("This feels quiet now."),
            _user("I want to stay present."),
        ]
    )

    assert result["stage"] == 2
    assert result["confidence"] == "LOW"
    assert result["score"] == 2
    assert result["signals"] == ["maybe i"]


def test_stage_uses_moderate_confidence_for_recent_single_signal() -> None:
    result = detect_stage([_user("Maybe I can be honest about this.")])

    assert result["stage"] == 2
    assert result["confidence"] == "MODERATE"
    assert result["score"] == 3


def test_stage_uses_high_confidence_for_multiple_recent_signals() -> None:
    result = detect_stage([_user("I trust myself, and I know what I need right now.")])

    assert result["stage"] == 4
    assert result["confidence"] == "HIGH"
    assert result["score"] == 6


def test_stage_deduplicates_repeated_signal_labels_across_messages() -> None:
    result = detect_stage(
        [
            _user("Maybe I can pause."),
            _user("Maybe I can listen."),
        ]
    )

    assert result["signals"] == ["maybe i"]
