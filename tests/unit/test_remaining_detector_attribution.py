"""Regression coverage for attribution across the remaining routed detectors."""

from soulmap.runtime.detectors.ancestral_detector import detect_ancestral
from soulmap.runtime.detectors.celebration_detector import detect_celebration
from soulmap.runtime.detectors.creative_drought_detector import detect_creative_drought
from soulmap.runtime.detectors.dark_night_detector import detect_dark_night
from soulmap.runtime.detectors.divine_guidance_detector import detect_divine_guidance
from soulmap.runtime.detectors.existential_detector import detect_existential
from soulmap.runtime.detectors.insight_detector import detect_insight
from soulmap.runtime.detectors.partnership_patterns_detector import (
    detect_partnership_patterns,
)
from soulmap.runtime.detectors.perfectionism_paralysis_detector import (
    detect_perfectionism_paralysis,
)
from soulmap.runtime.detectors.sacred_polarity_detector import detect_sacred_polarity
from soulmap.runtime.detectors.shadow_pattern_detector import detect_shadow_patterns
from soulmap.runtime.detectors.soul_nourishment_detector import detect_soul_nourishment
from soulmap.runtime.detectors.soulmate_longing_detector import detect_soulmate_longing
from soulmap.runtime.detectors.spiritual_bypass_detector import detect_bypass
from soulmap.runtime.detectors.spiritual_purpose_detector import detect_spiritual_purpose
from soulmap.runtime.routing.stage_detector import detect_stage


def test_attributed_third_party_signals_do_not_trigger_remaining_detectors() -> None:
    assert detect_ancestral("My friend said this runs in my family.")["ancestral_detected"] is False
    assert detect_dark_night("My friend said I feel spiritually empty and disconnected from everything.")["dark_night_detected"] is False
    assert detect_divine_guidance("My friend said I don't know if this is intuition or fear.")["divine_guidance_detected"] is False
    assert detect_creative_drought("My friend said I've lost my voice, I don't know what I want to say.")["creative_drought_detected"] is False
    assert detect_soulmate_longing("My friend said I'll never find my soulmate.")["soulmate_longing_detected"] is False
    assert detect_soul_nourishment("My friend said this feeds my soul.")["soul_nourishment_detected"] is False
    assert detect_spiritual_purpose("My friend said I'm waiting for certainty before I act.")["spiritual_purpose_detected"] is False
    assert detect_bypass("My friend said everything happens for a reason, so I shouldn't be attached.")["bypass_detected"] is False
    assert detect_partnership_patterns("My friend said I keep dating the same type of person.")["partnership_pattern_detected"] is False
    assert detect_celebration("My friend said I finally did it.")["celebration_detected"] is False
    assert detect_insight("My friend said I finally understand why I do this.")["insight_detected"] is False
    assert detect_existential("My friend said what is the point of any of this, why does any of this matter.")["existential_detected"] is False
    assert detect_shadow_patterns("My friend said I can't say no to people and always end up resenting it.")["shadow_detected"] is False
    assert detect_perfectionism_paralysis("My friend said it's never ready, nothing is ever good enough.")["perfectionism_paralysis_detected"] is False
    assert detect_sacred_polarity(
        "My friend said I value the balance of receptivity and action. I only know how to do, I don't know how to just be."
    )["sacred_polarity_detected"] is False
    assert detect_stage([{"role": "user", "content": "My friend said maybe I can be honest about this."}])["stage"] == 1


def test_attributed_history_does_not_add_existential_or_shadow_signals() -> None:
    existential = detect_existential(
        "I went for a walk this morning.",
        [{"role": "user", "content": "My friend said I don't recognize myself anymore."}],
    )
    shadow = detect_shadow_patterns(
        "I went for a walk this morning.",
        [{"role": "user", "content": "My friend said people always take advantage of me, it keeps happening."}],
    )

    assert existential["existential_detected"] is False
    assert shadow["shadow_detected"] is False


def test_attributed_history_does_not_supply_perfectionism_persistence() -> None:
    result = detect_perfectionism_paralysis(
        "People never meet my standards.",
        [{"role": "user", "content": "My friend said I'm still not ready to share this over and over."}],
    )

    assert result["perfectionism_paralysis_detected"] is False
    assert "pattern_persistence_in_history" not in result["signals"]


def test_attributed_history_does_not_enable_sacred_polarity_frame() -> None:
    result = detect_sacred_polarity(
        "I only know how to do, I don't know how to just be.",
        [{"role": "user", "content": "My friend said I value the balance of receptivity and action."}],
    )

    assert result["sacred_polarity_detected"] is False


def test_attributed_stage_signals_do_not_raise_conversation_stage() -> None:
    result = detect_stage(
        [
            {"role": "user", "content": "This is a neutral update."},
            {"role": "user", "content": "My friend said maybe I can be honest about this."},
        ]
    )

    assert result["stage"] == 1


def test_user_authored_signal_after_attributed_speech_remains_detectable() -> None:
    result = detect_dark_night(
        "My friend said I feel spiritually empty, but I feel spiritually empty too."
    )

    assert result["dark_night_detected"] is True
