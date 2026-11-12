"""Regression coverage for attribution in history-aware detectors and stage routing."""

from typing import cast

from soulmap.runtime.detectors.existential_detector import detect_existential
from soulmap.runtime.detectors.perfectionism_paralysis_detector import (
    detect_perfectionism_paralysis,
)
from soulmap.runtime.detectors.sacred_polarity_detector import detect_sacred_polarity
from soulmap.runtime.detectors.shadow_pattern_detector import detect_shadow_patterns
from soulmap.runtime.routing.stage_detector import detect_stage


def test_attributed_current_turn_signals_do_not_trigger_detectors() -> None:
    assert (
        detect_existential(
            "My friend said what is the point of any of this, "
            "why does any of this matter."
        )["existential_detected"]
        is False
    )
    assert (
        detect_shadow_patterns(
            "My friend said I can't say no to people and always end up resenting it."
        )["shadow_detected"]
        is False
    )
    assert (
        detect_perfectionism_paralysis(
            "My friend said it's never ready, nothing is ever good enough."
        )["perfectionism_paralysis_detected"]
        is False
    )
    assert (
        detect_sacred_polarity(
            "My friend said I value the balance of receptivity and action. "
            "I only know how to do, I don't know how to just be."
        )["sacred_polarity_detected"]
        is False
    )
    assert (
        detect_stage(
            [
                {
                    "role": "user",
                    "content": "My friend said maybe I can be honest about this.",
                }
            ]
        )["stage"]
        == 1
    )


def test_attributed_history_does_not_add_existential_or_shadow_signals() -> None:
    existential = detect_existential(
        "I went for a walk this morning.",
        [
            {
                "role": "user",
                "content": "My friend said I don't recognize myself anymore.",
            }
        ],
    )
    shadow = detect_shadow_patterns(
        "I went for a walk this morning.",
        [
            {
                "role": "user",
                "content": "My friend said people always take advantage of me, "
                "it keeps happening.",
            }
        ],
    )

    assert existential["existential_detected"] is False
    assert shadow["shadow_detected"] is False


def test_attributed_history_does_not_supply_perfectionism_persistence() -> None:
    result = detect_perfectionism_paralysis(
        "People never meet my standards.",
        [
            {
                "role": "user",
                "content": "My friend said I'm still not ready to share this "
                "over and over.",
            }
        ],
    )

    assert result["perfectionism_paralysis_detected"] is False
    signals = cast(list[str], result["signals"])
    assert "pattern_persistence_in_history" not in signals


def test_attributed_history_does_not_enable_sacred_polarity_frame() -> None:
    result = detect_sacred_polarity(
        "I only know how to do, I don't know how to just be.",
        [
            {
                "role": "user",
                "content": "My friend said I value the balance of receptivity "
                "and action.",
            }
        ],
    )

    assert result["sacred_polarity_detected"] is False


def test_attributed_stage_signals_do_not_raise_conversation_stage() -> None:
    result = detect_stage(
        [
            {"role": "user", "content": "This is a neutral update."},
            {
                "role": "user",
                "content": "My friend said maybe I can be honest about this.",
            },
        ]
    )

    assert result["stage"] == 1


def test_user_authored_signal_after_attributed_speech_remains_detectable() -> None:
    result = detect_existential(
        "My friend said I don't recognize myself anymore, "
        "but I don't recognize myself anymore either."
    )

    assert result["existential_detected"] is True
