"""Regression test for the sacred-polarity knowledge contract."""

import pytest

from soulmap.runtime.detectors import sacred_polarity_detector


def test_sacred_polarity_scoring_is_knowledge_authored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        sacred_polarity_detector._RULES, "Activation signal weight", "7"
    )
    result = sacred_polarity_detector.detect_sacred_polarity(
        sacred_polarity_detector.SACRED_POLARITY_SIGNALS[0]
    )
    assert result["score"] == 7
