from typing import cast

import pytest

from soulmap.runtime.detectors import crisis_detector


def test_non_crisis_farewell_context_does_not_escalate() -> None:
    result = crisis_detector.detect_crisis("Every day feels like goodbye.")

    assert result["level"] == "NO_CRISIS"
    assert result["tier"] == 0
    assert result["action"] == "CONTINUE_NORMAL"
    assert result["signals"] == []


def test_literal_farewell_crisis_signal_escalates_to_tier_one() -> None:
    result = crisis_detector.detect_crisis("I am saying goodbye.")

    assert result["level"] == "CRISIS_TIER1"
    assert result["tier"] == 1
    assert result["action"] == "IMMEDIATE_SAFETY_RESPONSE"
    signals = cast(list[str], result["signals"])
    assert "i am saying goodbye" in signals


def test_farewell_signal_is_not_appended_twice_when_tier_one_already_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(crisis_detector, "CRISIS_TIER1", ("i am saying goodbye",))

    result = crisis_detector.detect_crisis("I am saying goodbye.")

    assert result["level"] == "CRISIS_TIER1"
    assert result["tier"] == 1
    signals = cast(list[str], result["signals"])
    assert signals == ["i am saying goodbye"]
