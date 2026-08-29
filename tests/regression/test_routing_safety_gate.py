import pytest

from soulmap.runtime.routing import framework_selector

# Helper to install default non-triggering detector stubs
DEFAULTS = {
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
    "detect_patterns": {},
    "detect_stage": {"stage": 1},
}

SCENARIOS = [
    ("CRISIS", {"detect_crisis": {"tier": 1}}),
    ("DEPENDENCY", {"analyze_dependency": {"level": "HIGH_DEPENDENCY"}}),
    ("DE_ESCALATION", {"detect_intensity": {"level": "HIGH"}}),
    (
        "DE_ESCALATION",
        {
            "detect_intensity": {"level": "MODERATE"},
            "detect_insight": {"insight_detected": True},
        },
    ),
    ("GRIEF", {"detect_grief": {"grief_detected": True, "grief_type": "acute"}}),
    ("EXISTENTIAL", {"detect_existential": {"existential_detected": True}}),
    ("INNER_PARTS", {"detect_inner_conflict": {"conflict_detected": True}}),
    ("DIRECTION", {"detect_direction_need": {"direction_detected": True}}),
    (
        "CREATIVE_DROUGHT",
        {"detect_creative_drought": {"creative_drought_detected": True}},
    ),
    (
        "PERFECTIONISM_PARALYSIS",
        {"detect_perfectionism_paralysis": {"perfectionism_paralysis_detected": True}},
    ),
    ("SHADOW", {"detect_shadow_patterns": {"shadow_detected": True}}),
    ("ANCESTRAL_PATTERNS", {"detect_ancestral": {"ancestral_detected": True}}),
    (
        "FEAR_OF_VISIBILITY",
        {"detect_visibility_fear": {"visibility_fear_detected": True}},
    ),
    ("EMPATH_BOUNDARY", {"detect_empath_overwhelm": {"empath_detected": True}}),
    ("DARK_NIGHT_OF_SOUL", {"detect_dark_night": {"dark_night_detected": True}}),
    (
        "SOUL_NOURISHMENT",
        {"detect_soul_nourishment": {"soul_nourishment_detected": True}},
    ),
    (
        "DIVINE_GUIDANCE",
        {"detect_divine_guidance": {"divine_guidance_detected": True}},
    ),
    (
        "SACRED_POLARITY",
        {"detect_sacred_polarity": {"sacred_polarity_detected": True}},
    ),
    (
        "SPIRITUAL_PURPOSE",
        {"detect_spiritual_purpose": {"spiritual_purpose_detected": True}},
    ),
    ("INTEGRATION_CELEBRATION", {"detect_celebration": {"celebration_detected": True}}),
    ("MEANING_INTEGRATION", {"detect_insight": {"insight_detected": True}}),
    (
        "SYNTHESIS",
        {"_analyze_synthesis": {"synthesis_triggered": True, "synthesis_ready": True}},
    ),
    (
        "PATTERN",
        {"detect_patterns": {"primary_pattern": "repeating", "wait_for_more": False}},
    ),
    ("MIRROR", {}),
]


def _install_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch every detector import in framework_selector to safe defaults
    for name, value in DEFAULTS.items():
        if hasattr(framework_selector, name):
            monkeypatch.setattr(framework_selector, name, lambda *a, _v=value, **k: _v)

    # _analyze_synthesis used via task — stub to quiet synth
    if hasattr(framework_selector, "_analyze_synthesis"):
        monkeypatch.setattr(
            framework_selector,
            "_analyze_synthesis",
            lambda *a, **k: {"synthesis_triggered": False},
        )


@pytest.mark.parametrize(("expected_primary", "overrides"), SCENARIOS)
def test_every_routing_path_calls_safety_gate(
    monkeypatch: pytest.MonkeyPatch,
    expected_primary: str,
    overrides: dict[str, object],
) -> None:
    """For each selector outcome, ensure the Safety Gate is invoked and its status surfaces."""
    _install_defaults(monkeypatch)

    # Apply scenario-specific overrides
    for name, value in overrides.items():
        # allow overriding the _analyze_synthesis helper
        if hasattr(framework_selector, name):
            monkeypatch.setattr(framework_selector, name, lambda *a, _v=value, **k: _v)
        else:
            # fallback: set attribute even if missing
            setattr(framework_selector, name, lambda *a, _v=value, **k: _v)

    called = {"count": 0, "args": None}

    def fake_apply_safety_gate(
        message: str,
        history: list[dict[str, str]],
        memory: dict[str, object] | None,
        selection: dict[str, object],
    ) -> dict[str, object]:
        called["count"] += 1
        called["args"] = (message, history, memory, selection)
        # return a simple pass-through gated result
        return {"status": "ok", "reason": "allowed", "selection": selection}

    monkeypatch.setattr(framework_selector, "apply_safety_gate", fake_apply_safety_gate)

    # Run selection
    history = (
        [{"role": "user", "content": "hi"}] if "detect_patterns" in overrides else []
    )
    result = framework_selector.select_framework("hi", history)

    assert called["count"] == 1, (
        f"Safety Gate was not called for scenario {expected_primary}"
    )
    assert result.get("safety_status") == "ok"
    # primary framework should match expected (some scenarios share primary)
    assert result.get("primary_framework") == expected_primary


def test_safety_gate_overrides_tier1_crisis_when_selector_misses_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gate must re-derive Tier 1 crisis from the raw message independently."""
    _install_defaults(monkeypatch)
    monkeypatch.setattr(
        framework_selector,
        "detect_crisis",
        lambda *_args, **_kwargs: {"tier": 0},
    )

    result = framework_selector.select_framework("I want to kill myself.", [])

    assert result["primary_framework"] == "CRISIS"
    assert result["safety_status"] == "OVERRIDE"
    assert result["safety_reason"] == "tier1_crisis"
    assert result["safety_flags"] == ["crisis"]


def test_safety_gate_overrides_tier1_crisis_when_the_detector_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gate must still catch crisis when the selector's detector crashes.

    This is a different failure path from the miss above. A miss returns a
    wrong but valid result, while a crash goes through
    `_run_detector_async`, which swallows the exception and substitutes an
    empty result so one broken detector cannot fail the whole request. That
    degraded path must not lose the Tier 1 override, which is the property
    ADR 0001 exists to guarantee.
    """
    _install_defaults(monkeypatch)

    def exploding_detector(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise RuntimeError("crisis detector is down")

    monkeypatch.setattr(framework_selector, "detect_crisis", exploding_detector)

    result = framework_selector.select_framework("I want to kill myself.", [])

    assert result["primary_framework"] == "CRISIS"
    assert result["safety_status"] == "OVERRIDE"
    assert result["safety_reason"] == "tier1_crisis"
    assert result["safety_flags"] == ["crisis"]


def test_grief_outranks_moderate_intensity_de_escalation() -> None:
    """Expressing distress must not cost a grieving user the grief framework.

    orchestration.md reserves "force De-escalation as primary regardless of
    topic" for HIGH intensity. MODERATE says "apply slow-down mode, hold
    framework lightly", and its priority table lists Grief above
    De-escalation (MODERATE) under a first-match-wins rule.

    The moderate branch used to demote grief to a secondary layer, so adding
    an intensity marker to a loss took grief-companion.md away and swapped
    sanctuary mode for a reply that ends with a question. The more the person
    was crying, the less grief support they got.
    """
    quiet = framework_selector.select_framework("My dog died this morning", [])
    distressed = framework_selector.select_framework(
        "My dog died this morning and I cannot stop crying", []
    )

    assert quiet["primary_framework"] == "GRIEF"
    assert distressed["primary_framework"] == "GRIEF"
    assert distressed["mode"] == "SANCTUARY"


def test_moderate_intensity_without_grief_still_de_escalates() -> None:
    """The grief branch must not swallow plain moderate-intensity routing."""
    result = framework_selector.select_framework(
        "I cannot think anymore, everything is spinning, I do not know what to do", []
    )

    assert result["primary_framework"] == "DE_ESCALATION"


def test_high_intensity_still_forces_de_escalation_over_grief() -> None:
    """HIGH intensity keeps its override, which doctrine states explicitly."""
    result = framework_selector.select_framework(
        "My dog died and I can't breathe, everything is falling apart, "
        "I can't stop shaking",
        [],
    )

    assert result["primary_framework"] == "DE_ESCALATION"
    assert result["mode"] == "SANCTUARY"
