"""Focused regression tests for knowledge-authored detector contracts."""

from __future__ import annotations

import pytest

from soulmap.runtime.detectors import (
    ancestral_detector,
    anger_detector,
    existential_detector,
    grief_detector,
    inner_conflict_detector,
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
    result = spiritual_bypass_detector.detect_bypass("everything happens for a reason")
    assert result["score"] == 7


def test_shadow_detector_uses_knowledge_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        shadow_pattern_detector._SHADOW_SCORING, "Minimum detection score", "99"
    )
    result = shadow_pattern_detector.detect_shadow_patterns(
        "people always take advantage of me"
    )
    assert result["shadow_detected"] is False


def test_ancestral_detector_uses_knowledge_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        ancestral_detector._ANCESTRAL_SCORING, "Minimum detection score", "99"
    )
    result = ancestral_detector.detect_ancestral("this runs in my family")
    assert result["ancestral_detected"] is False


def test_existential_response_policy_is_markdown_authored() -> None:
    result = existential_detector.detect_existential(
        "I don't recognize myself anymore."
    )
    recommendation = result["recommendation"]
    assert isinstance(recommendation, str)
    assert "Do NOT provide philosophical conclusions." in recommendation
    assert "Existential Reflection Companion" in recommendation


def test_insight_response_policy_is_markdown_authored() -> None:
    result = insight_detector.detect_insight("I finally understand why I do this.")
    recommendation = result["recommendation"]
    assert isinstance(recommendation, str)
    assert "Do NOT prescribe change." in recommendation
    assert "Meaning Integration Guide" in recommendation


def test_inner_parts_suffix_is_markdown_authored() -> None:
    result = inner_conflict_detector.detect_inner_conflict(
        "Part of me wants to leave, but another part is scared."
    )
    assert result["parts_suggested"]
    recommendation = result["recommendation"]
    assert isinstance(recommendation, str)
    assert "Likely parts present:" in recommendation


def test_grief_response_policy_is_markdown_authored() -> None:
    result = grief_detector.detect_grief("My mother died yesterday.")
    recommendation = result["recommendation"]
    assert isinstance(recommendation, str)
    assert "Activate grief-companion.md." in recommendation
    assert "Grief Questions" in recommendation
