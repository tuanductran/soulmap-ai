"""Contract regression tests for grief, somatic, and intensity policy."""

from collections.abc import Callable
from types import ModuleType

import pytest

from soulmap.runtime.detectors import (
    emotional_intensity_detector,
    grief_detector,
    somatic_detector,
)


@pytest.mark.parametrize(
    ("module", "key", "detector", "signal"),
    [
        (
            grief_detector,
            "Acute grief weight",
            grief_detector.detect_grief,
            grief_detector.ACUTE_GRIEF[0],
        ),
        (
            somatic_detector,
            "Biometric context weight",
            somatic_detector.detect_somatic,
            somatic_detector.BIOMETRIC[0],
        ),
        (
            emotional_intensity_detector,
            "Physical overwhelm weight",
            emotional_intensity_detector.detect_intensity,
            emotional_intensity_detector.PHYSICAL_OVERWHELM[0],
        ),
    ],
)
def test_detector_policy_is_knowledge_authored(
    module: ModuleType,
    key: str,
    detector: Callable[[str], dict[str, object]],
    signal: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(module._RULES, key, "7")
    result = detector(signal)
    assert result["score"] == 7
