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


def _install_defaults(monkeypatch):
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


@pytest.mark.parametrize("expected_primary,overrides", SCENARIOS)
def test_every_routing_path_calls_safety_gate(monkeypatch, expected_primary, overrides):
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

    def fake_apply_safety_gate(message, history, memory, selection):
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
