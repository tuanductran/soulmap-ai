"""Regression coverage for reviewed non-English spiritual-bypass evidence."""

from __future__ import annotations

import pytest

from soulmap.runtime.detectors.spiritual_bypass_detector import detect_bypass


@pytest.mark.parametrize(
    ("message", "bypass_type"),
    [
        ("Todo pasa por algo, así que no debería estar apegado.", "dismissing_pain"),
        ("Je suis en paix avec ça, je leur ai déjà pardonné.", "premature_acceptance"),
        (
            "作为一个共情者我能感受到\uff0c大多数人无法理解我。",
            "spiritual_inflation",
        ),
        ("그들은 나의 스승이었어. 우주가 그들을 보냈어.", "bypassing_accountability"),
    ],
)
def test_reviewed_locale_phrase_is_detected(message: str, bypass_type: str) -> None:
    result = detect_bypass(message)

    assert result["bypass_detected"] is True
    assert result["bypass_type"] == bypass_type


@pytest.mark.parametrize(
    "message",
    [
        "Estoy triste y todavía intento entender lo que pasó.",
        "Je suis triste et j'essaie encore de comprendre ce qui s'est passé.",
        "我很难过\uff0c还在试着理解发生了什么。",
        "나는 슬프고 아직 무슨 일이 일어났는지 이해하려고 해.",
    ],
)
def test_near_miss_without_reviewed_phrase_is_not_flagged(message: str) -> None:
    result = detect_bypass(message)

    assert result["bypass_detected"] is False
    assert result["bypass_type"] is None
