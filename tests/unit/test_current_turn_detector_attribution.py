"""Regression coverage for attribution in current-turn routed detectors."""

from soulmap.runtime.detectors.ancestral_detector import detect_ancestral
from soulmap.runtime.detectors.celebration_detector import detect_celebration
from soulmap.runtime.detectors.creative_drought_detector import detect_creative_drought
from soulmap.runtime.detectors.dark_night_detector import detect_dark_night
from soulmap.runtime.detectors.divine_guidance_detector import detect_divine_guidance
from soulmap.runtime.detectors.insight_detector import detect_insight
from soulmap.runtime.detectors.partnership_patterns_detector import (
    detect_partnership_patterns,
)
from soulmap.runtime.detectors.soul_nourishment_detector import detect_soul_nourishment
from soulmap.runtime.detectors.soulmate_longing_detector import detect_soulmate_longing
from soulmap.runtime.detectors.spiritual_bypass_detector import detect_bypass
from soulmap.runtime.detectors.spiritual_purpose_detector import detect_spiritual_purpose


def test_attributed_third_party_signals_do_not_trigger_detectors() -> None:
    assert (
        detect_ancestral("My friend said this runs in my family.")[
            "ancestral_detected"
        ]
        is False
    )
    assert (
        detect_dark_night(
            "My friend said I feel spiritually empty and disconnected from everything."
        )["dark_night_detected"]
        is False
    )
    assert (
        detect_divine_guidance(
            "My friend said I don't know if this is intuition or fear."
        )["divine_guidance_detected"]
        is False
    )
    assert (
        detect_creative_drought(
            "My friend said I've lost my voice, I don't know what I want to say."
        )["creative_drought_detected"]
        is False
    )
    assert (
        detect_soulmate_longing("My friend said I'll never find my soulmate.")[
            "soulmate_longing_detected"
        ]
        is False
    )
    assert (
        detect_soul_nourishment("My friend said this feeds my soul.")[
            "soul_nourishment_detected"
        ]
        is False
    )
    assert (
        detect_spiritual_purpose(
            "My friend said I'm waiting for certainty before I act."
        )["spiritual_purpose_detected"]
        is False
    )
    assert (
        detect_bypass(
            "My friend said everything happens for a reason, so I shouldn't be attached."
        )["bypass_detected"]
        is False
    )
    assert (
        detect_partnership_patterns(
            "My friend said I keep dating the same type of person."
        )["partnership_pattern_detected"]
        is False
    )
    assert (
        detect_celebration("My friend said I finally did it.")[
            "celebration_detected"
        ]
        is False
    )
    assert (
        detect_insight("My friend said I finally understand why I do this.")[
            "insight_detected"
        ]
        is False
    )


def test_user_authored_signal_after_reported_speech_remains_detectable() -> None:
    result = detect_dark_night(
        "My friend said I feel spiritually empty, "
        "but I feel spiritually empty too."
    )

    assert result["dark_night_detected"] is True
