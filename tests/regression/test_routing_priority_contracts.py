import pytest

from soulmap.runtime.routing import framework_selector

_DEFAULTS = {
    "detect_crisis": {"tier": 0},
    "analyze_dependency": {"level": "NORMAL"},
    "detect_intensity": {"level": "NORMAL"},
    "detect_somatic": {"somatic_detected": False},
    "detect_anger": {"anger_detected": False},
    "detect_bypass": {"bypass_detected": False},
    "detect_insight": {"insight_detected": False},
    "detect_grief": {"grief_detected": False},
    "detect_inner_conflict": {"conflict_detected": False},
    "detect_direction_need": {"direction_detected": False},
    "detect_creative_drought": {"creative_drought_detected": False},
    "detect_perfectionism_paralysis": {"perfectionism_paralysis_detected": False},
    "detect_shadow_patterns": {"shadow_detected": False},
    "detect_ancestral": {"ancestral_detected": False},
    "detect_visibility_fear": {"visibility_fear_detected": False},
    "detect_empath_overwhelm": {"empath_detected": False},
    "detect_celebration": {"celebration_detected": False},
    "detect_dark_night": {"dark_night_detected": False},
    "detect_soul_nourishment": {"soul_nourishment_detected": False},
    "detect_divine_guidance": {"divine_guidance_detected": False},
    "detect_sacred_polarity": {"sacred_polarity_detected": False},
    "detect_spiritual_purpose": {"spiritual_purpose_detected": False},
    "detect_soulmate_longing": {"soulmate_longing_detected": False},
    "detect_partnership_patterns": {"partnership_pattern_detected": False},
    "detect_existential": {"existential_detected": False},
    "detect_patterns": {},
    "detect_stage": {"stage": 1},
}


def _install(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in _DEFAULTS.items():
        if hasattr(framework_selector, name):
            monkeypatch.setattr(
                framework_selector,
                name,
                lambda *args, _value=value, **kwargs: _value,
            )
    monkeypatch.setattr(
        framework_selector,
        "_analyze_synthesis",
        lambda *args, **kwargs: {"synthesis_triggered": False},
    )
    monkeypatch.setattr(
        framework_selector,
        "apply_safety_gate",
        lambda message, history, memory, selection: {
            "status": "ok",
            "reason": "allowed",
            "flags": [],
            "selection": selection,
        },
    )


def test_stage_one_first_message_forces_mirror(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    monkeypatch.setattr(
        framework_selector,
        "detect_grief",
        lambda *args, **kwargs: {"grief_detected": True, "grief_type": "acute"},
    )
    result = framework_selector.select_framework("My father died yesterday.", [])
    assert result["primary_framework"] == "MIRROR"
    assert result["mode"] == "MIRROR"


def test_stage_one_second_message_forces_mirror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install(monkeypatch)
    monkeypatch.setattr(
        framework_selector,
        "detect_existential",
        lambda *args, **kwargs: {"existential_detected": True},
    )
    result = framework_selector.select_framework(
        "What is the point of all this?",
        [{"role": "user", "content": "I have been thinking a lot."}],
    )
    assert result["primary_framework"] == "MIRROR"
    assert result["mode"] == "MIRROR"


def test_high_intensity_has_no_secondary_layer(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    monkeypatch.setattr(
        framework_selector,
        "detect_intensity",
        lambda *args, **kwargs: {"level": "HIGH"},
    )
    monkeypatch.setattr(
        framework_selector,
        "detect_anger",
        lambda *args, **kwargs: {"anger_detected": True},
    )
    monkeypatch.setattr(
        framework_selector,
        "detect_bypass",
        lambda *args, **kwargs: {"bypass_detected": True},
    )
    monkeypatch.setattr(
        framework_selector,
        "detect_somatic",
        lambda *args, **kwargs: {"somatic_detected": True},
    )
    result = framework_selector.select_framework("Everything feels overwhelming.", [])
    assert result["primary_framework"] == "DE_ESCALATION"
    assert result["mode"] == "SANCTUARY"
    assert result["secondary_layer"] is None


def test_strong_breakthrough_outranks_grief(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    monkeypatch.setattr(
        framework_selector,
        "detect_insight",
        lambda *args, **kwargs: {"insight_detected": True, "strength": "strong"},
    )
    monkeypatch.setattr(
        framework_selector,
        "detect_grief",
        lambda *args, **kwargs: {"grief_detected": True, "grief_type": "acute"},
    )
    result = framework_selector.select_framework(
        "I suddenly understand what has been happening all this time.",
        [{"role": "user", "content": "I have been reflecting."}],
    )
    assert result["primary_framework"] == "MEANING_INTEGRATION"
    assert result["secondary_layer"] is None


def test_high_intensity_outranks_insight(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    monkeypatch.setattr(
        framework_selector,
        "detect_intensity",
        lambda *args, **kwargs: {"level": "HIGH"},
    )
    monkeypatch.setattr(
        framework_selector,
        "detect_insight",
        lambda *args, **kwargs: {"insight_detected": True, "strength": "strong"},
    )
    result = framework_selector.select_framework(
        "I see everything clearly but I am overwhelmed.", []
    )
    assert result["primary_framework"] == "DE_ESCALATION"
    assert result["secondary_layer"] is None
