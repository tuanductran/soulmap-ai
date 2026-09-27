"""Regression tests for remaining knowledge-authored detector contracts."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

import pytest

class DetectorModule(Protocol):
    _RULES: dict[str, str]


Detector = Callable[[str], dict[str, object]]


from soulmap.runtime.detectors import (
    creative_drought_detector,
    dark_night_detector,
    divine_guidance_detector,
    empath_detector,
    inner_conflict_detector,
    partnership_patterns_detector,
    perfectionism_paralysis_detector,
    soulmate_longing_detector,
    soul_nourishment_detector,
    spiritual_purpose_detector,
    visibility_fear_detector,
)


@pytest.mark.parametrize(
    ("module", "detector", "signal_name", "weight_key"),
    [
        (empath_detector, empath_detector.detect_empath_overwhelm, "EMPATH_SIGNALS", "Activation signal weight"),
        (dark_night_detector, dark_night_detector.detect_dark_night, "DARK_NIGHT_SIGNALS", "Activation signal weight"),
        (divine_guidance_detector, divine_guidance_detector.detect_divine_guidance, "DIVINE_GUIDANCE_SIGNALS", "Activation signal weight"),
        (visibility_fear_detector, visibility_fear_detector.detect_visibility_fear, "VISIBILITY_FEAR_SIGNALS", "Direct visibility-fear weight"),
        (soulmate_longing_detector, soulmate_longing_detector.detect_soulmate_longing, "SOULMATE_LONGING_SIGNALS", "Activation signal weight"),
        (creative_drought_detector, creative_drought_detector.detect_creative_drought, "CREATIVE_DROUGHT_SIGNALS", "Activation signal weight"),
        (soul_nourishment_detector, soul_nourishment_detector.detect_soul_nourishment, "SOUL_NOURISHMENT_SIGNALS", "Activation signal weight"),
        (spiritual_purpose_detector, spiritual_purpose_detector.detect_spiritual_purpose, "SPIRITUAL_PURPOSE_SIGNALS", "Activation signal weight"),
        (partnership_patterns_detector, partnership_patterns_detector.detect_partnership_patterns, "PARTNERSHIP_PATTERNS_SIGNALS", "Activation signal weight"),
        (perfectionism_paralysis_detector, perfectionism_paralysis_detector.detect_perfectionism_paralysis, "PERFECTIONISM_PARALYSIS_SIGNALS", "Paralysis signal weight"),
        (inner_conflict_detector, inner_conflict_detector.detect_inner_conflict, "EXPLICIT_CONFLICT", "Explicit-conflict weight"),
    ],
)
def test_detector_scoring_is_knowledge_authored(
    module: DetectorModule,
    detector: Detector,
    signal_name: str,
    weight_key: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signals = getattr(module, signal_name)
    assert signals

    monkeypatch.setitem(module._RULES, weight_key, "7")
    result = detector(signals[0])
    assert result["score"] == 7
