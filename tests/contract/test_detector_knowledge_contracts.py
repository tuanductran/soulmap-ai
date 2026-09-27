"""Focused regression tests for knowledge-authored detector contracts."""

from __future__ import annotations

import pytest

from soulmap.runtime.detectors import (
    ancestral_detector,
    anger_detector,
    existential_detector,
    insight_detector,
    shadow_pattern_detector,
    spiritual_bypass_detector,
)


def test_insight_detector_uses_knowledge_scoring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        insight_detector._INSIGHT_SCORING, "Explicit insight weight", "7"
    )
    result = insight_detector.detect_insight("i finally understand")
    assert result["score"] == 7


def test_existential_detector_uses_knowledge_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        existential_detector._EXISTENTIAL_SCORING, "Minimum detection score", "99"
    )
    result = existential_detector.detect_existential(
        "i do not recognize myself anymore"
    )
    assert result["existential_detected"] is False


def test_anger_detector_uses_knowledge_scoring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(anger_detector._ANGER_SCORING, "Active anger weight", "7")
    result = anger_detector.detect_anger("this makes me furious")
    assert result["score"] == 7


def test_bypass_detector_uses_knowledge_scoring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        spiritual_bypass_detector._BYPASS_SCORING,
        "Dismissing-pain weight",
        "7",
    )
    result = spiritual_bypass_detector.detect_bypass("pain is an illusion")
    assert result["score"] == 7


def test_shadow_detector_uses_knowledge_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(shadow_pattern_detector._SHADOW_SCORING, "Minimum detection score", "99")
    result = shadow_pattern_detector.detect_shadow_patterns(
        "people always take advantage of me"
    )
    assert result["shadow_detected"] is False


def test_ancestral_detector_uses_knowledge_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(ancestral_detector._ANCESTRAL_SCORING, "Minimum detection score", "99")
    result = ancestral_detector.detect_ancestral("this runs in my family")
    assert result["ancestral_detected"] is False
