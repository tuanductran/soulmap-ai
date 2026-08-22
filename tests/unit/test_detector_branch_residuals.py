from __future__ import annotations

from typing import cast

import pytest

from soulmap.runtime.detectors import (
    anger_detector,
    celebration_detector,
    pattern_detector,
)
from soulmap.runtime.knowledge.pattern_source import PatternSignal


def test_pattern_detector_deduplicates_repeated_keyword_and_cycle_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        pattern_detector,
        "PATTERN_SIGNALS",
        {
            "example": PatternSignal(
                slug="example",
                name="Example",
                description="Example pattern",
                keywords=("repeat", "repeat"),
                cycle_phrases=("loop", "loop"),
                soulmap_role="Reflect the repeated thread.",
                reflection_language=("Notice the pattern.",),
            )
        },
    )

    result = pattern_detector.detect_patterns(
        [
            {"role": "user", "content": "repeat loop"},
            {"role": "user", "content": "repeat loop"},
        ]
    )

    assert result["primary_pattern"] == "example"
    detected = cast(list[dict[str, object]], result["patterns_detected"])
    assert detected[0]["score"] == 10
    assert detected[0]["signals"] == ["repeat", "[cycle] loop"]


def test_anger_detector_keeps_active_type_when_residual_signal_also_matches() -> None:
    active = anger_detector.ACTIVE_ANGER[0]
    residual = anger_detector.RESIDUAL_ANGER[0]

    result = anger_detector.detect_anger(f"{active} {residual}")

    assert result["anger_detected"] is True
    assert result["anger_type"] == "active"
    assert result["score"] == 5
    signals = cast(list[str], result["signals"])
    assert any(signal.startswith("residual:") for signal in signals)


def test_anger_detector_does_not_mark_single_recent_signal_as_sustained() -> None:
    active = anger_detector.ACTIVE_ANGER[0]

    result = anger_detector.detect_anger(
        active,
        [{"role": "user", "content": active}],
    )

    assert result["anger_detected"] is True
    assert result["score"] == 3
    signals = cast(list[str], result["signals"])
    assert "sustained_anger_across_messages" not in signals


def test_celebration_without_history_skips_confirmation_lookup() -> None:
    result = celebration_detector.detect_celebration("I finally did it.", [])

    assert result["celebration_detected"] is True
    assert result["has_negative_override"] is False
    signals = cast(list[str], result["signals"])
    assert "confirms_celebration_reflection" not in signals


def test_celebration_confirmation_requires_matching_assistant_reflection() -> None:
    result = celebration_detector.detect_celebration(
        "Yes, I finally did it.",
        [{"role": "assistant", "content": "Let us discuss another topic."}],
    )

    assert result["celebration_detected"] is True
    signals = cast(list[str], result["signals"])
    assert "confirms_celebration_reflection" not in signals


def test_celebration_confirmation_adds_score_after_matching_reflection() -> None:
    result = celebration_detector.detect_celebration(
        "Yes, I finally did it.",
        [{"role": "assistant", "content": "Let it land before moving on."}],
    )

    signals = cast(list[str], result["signals"])
    assert "confirms_celebration_reflection" in signals
    assert result["score"] == 5


def test_celebration_classifier_falls_back_to_general_positive() -> None:
    assert celebration_detector._classify_celebration_type("neutral update") == (
        "general_positive"
    )


def test_celebration_uses_general_positive_instruction_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        celebration_detector,
        "_classify_celebration_type",
        lambda _message: "general_positive",
    )

    result = celebration_detector.detect_celebration("I finally did it.")

    assert result["celebration_detected"] is True
    assert result["celebration_type"] == "general_positive"
    recommendation = cast(str, result["recommendation"])
    assert "After a breakthrough" in recommendation
