"""Verify Python-owned routing configuration and natural-language mode guidance."""

import pytest

from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules
from soulmap.runtime.knowledge.runtime_config import ORCHESTRATION_CONFIG
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path


def test_orchestration_runtime_contract_loads() -> None:
    """Verify the shipped orchestration contract loads successfully."""
    rules = load_orchestration_rules()

    assert rules.stage_1_max_user_messages == 2
    assert rules.breakthrough_min_strength == "strong"
    assert rules.phase_1_safety_before_framework_selection is True
    assert rules.template_routing_required is True
    assert rules.peer_min_stage == 5
    assert len({rule.framework for rule in rules.primary_priority}) == len(
        rules.primary_priority
    )
    assert len({rule.name for rule in rules.secondary_priority}) == len(
        rules.secondary_priority
    )
    assert len({rule.level for rule in rules.intensity_fallback}) == len(
        rules.intensity_fallback
    )
    assert [
        (rule.level, rule.framework, rule.mode) for rule in rules.intensity_fallback
    ] == [
        ("HIGH", "DE_ESCALATION", "SANCTUARY"),
        ("MODERATE", "DE_ESCALATION", "MIRROR"),
    ]

    assert [rule.framework for rule in rules.primary_priority] == [
        "GRIEF",
        "EXISTENTIAL",
        "INNER_PARTS",
        "DIRECTION",
        "CREATIVE_DROUGHT",
        "PERFECTIONISM_PARALYSIS",
        "SHADOW",
        "ANCESTRAL_PATTERNS",
        "FEAR_OF_VISIBILITY",
        "EMPATH_BOUNDARY",
        "DARK_NIGHT_OF_SOUL",
        "SOUL_NOURISHMENT",
        "DIVINE_GUIDANCE",
        "SACRED_POLARITY",
        "SPIRITUAL_PURPOSE",
        "SOULMATE_LONGING",
        "PARTNERSHIP_PATTERNS",
        "INTEGRATION_CELEBRATION",
        "MEANING_INTEGRATION",
        "SYNTHESIS",
        "PATTERN",
    ]
    assert [rule.name for rule in rules.secondary_priority] == [
        "anger",
        "bypass",
        "somatic",
    ]
    assert all(not hasattr(rule, "result") for rule in rules.primary_priority)
    assert all(not hasattr(rule, "detected") for rule in rules.primary_priority)
    assert all(not hasattr(rule, "result") for rule in rules.secondary_priority)
    assert all(not hasattr(rule, "detected") for rule in rules.secondary_priority)


def test_orchestration_runtime_instructions_are_knowledge_authored() -> None:
    rules = load_orchestration_rules()

    assert rules.runtime_instructions == {
        "stage_1_override": "Stage 1 first-contact override. Use minimal-depth presence and reflection; do not activate a framework.",
        "high_emotional_intensity": "Sanctuary mode. Acknowledge, ground, and normalize. Do not use a five-step framework or ask an inquiry question. Keep the response brief and proportionate.",
        "moderate_emotional_intensity": "Hold the framework lightly and slow the conversation before deeper reflection.",
        "mirror_mode_fallback": "Use the response-structure arc and, when appropriate, end with at most one question from deep-inquiry-bank.md. Respect mode, safety, and user readiness; zero questions is valid when a question would add pressure.",
        "peer_mode_fallback": "Use dialogue and light structure, with at most one question when it supports the conversation. Do not force a question merely to satisfy the format.",
    }


def test_detector_bindings_cover_every_markdown_framework() -> None:
    from soulmap.runtime.routing.framework_selector import (
        _primary_detector_binding,
        _secondary_detector_binding,
    )

    rules = load_orchestration_rules()
    expected_primary = {
        "GRIEF": ("grief", "grief_detected", None, None),
        "EXISTENTIAL": ("existential", "existential_detected", None, None),
        "INNER_PARTS": ("conflict", "conflict_detected", None, None),
        "DIRECTION": ("direction", "direction_detected", None, None),
        "CREATIVE_DROUGHT": (
            "creative_drought",
            "creative_drought_detected",
            None,
            None,
        ),
        "PERFECTIONISM_PARALYSIS": (
            "perfectionism",
            "perfectionism_paralysis_detected",
            None,
            None,
        ),
        "SHADOW": ("shadow", "shadow_detected", None, None),
        "ANCESTRAL_PATTERNS": ("ancestral", "ancestral_detected", None, None),
        "FEAR_OF_VISIBILITY": (
            "visibility_fear",
            "visibility_fear_detected",
            None,
            None,
        ),
        "EMPATH_BOUNDARY": ("empath", "empath_detected", None, None),
        "DARK_NIGHT_OF_SOUL": ("dark_night", "dark_night_detected", None, None),
        "SOUL_NOURISHMENT": (
            "soul_nourishment",
            "soul_nourishment_detected",
            None,
            None,
        ),
        "DIVINE_GUIDANCE": ("divine_guidance", "divine_guidance_detected", None, None),
        "SACRED_POLARITY": ("sacred_polarity", "sacred_polarity_detected", None, None),
        "SPIRITUAL_PURPOSE": (
            "spiritual_purpose",
            "spiritual_purpose_detected",
            None,
            None,
        ),
        "SOULMATE_LONGING": (
            "soulmate_longing",
            "soulmate_longing_detected",
            None,
            None,
        ),
        "PARTNERSHIP_PATTERNS": (
            "partnership_patterns",
            "partnership_pattern_detected",
            None,
            None,
        ),
        "INTEGRATION_CELEBRATION": ("celebration", "celebration_detected", None, None),
        "MEANING_INTEGRATION": ("insight", "insight_detected", None, None),
        "SYNTHESIS": ("synthesis", "synthesis_triggered", "synthesis_ready", None),
        "PATTERN": ("pattern", "primary_pattern", None, "wait_for_more"),
    }
    expected_secondary = {
        "anger": ("anger", "anger_detected"),
        "bypass": ("bypass", "bypass_detected"),
        "somatic": ("somatic", "somatic_detected"),
    }

    assert set(expected_primary) == {rule.framework for rule in rules.primary_priority}
    assert set(expected_secondary) == {rule.name for rule in rules.secondary_priority}
    assert {
        rule.framework: _primary_detector_binding(rule.framework)
        for rule in rules.primary_priority
    } == expected_primary
    assert {
        rule.name: _secondary_detector_binding(rule.name)
        for rule in rules.secondary_priority
    } == expected_secondary


def test_detector_bindings_reject_unknown_names() -> None:
    import pytest

    from soulmap.runtime.routing.framework_selector import (
        _primary_detector_binding,
        _secondary_detector_binding,
    )

    with pytest.raises(ValueError, match="Unknown primary framework binding"):
        _primary_detector_binding("UNKNOWN")
    with pytest.raises(ValueError, match="Unknown secondary detector binding"):
        _secondary_detector_binding("unknown")


def test_routing_policy_uses_human_readable_names() -> None:
    """Verify routing output uses human-readable labels."""
    text = runtime_skill_path("orchestration").read_text(encoding="utf-8")
    policy = text.split("## Routing policy", 1)[1].split("## Decision Tree", 1)[0]

    for token in ("DE_ESCALATION", "INNER_PARTS", "meaning_integration", "inner_parts"):
        assert token not in policy
    assert "### Operational limits" not in policy
    assert "### Primary framework priority" not in policy
    assert "### Secondary layer priority" not in policy
    assert "### Intensity fallback" not in policy
    assert "Mode guidance" in policy


def test_orchestration_rejects_unknown_breakthrough_strength(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    load_orchestration_rules.cache_clear()
    monkeypatch.setitem(
        ORCHESTRATION_CONFIG["scalars"],
        "Breakthrough minimum insight strength",
        "unexpected",
    )

    with pytest.raises(ValueError, match="must be one of: emerging, strong"):
        load_orchestration_rules()

    load_orchestration_rules.cache_clear()


def test_phase_one_safety_overrides_precede_framework_selection() -> None:
    """Keep immediate crisis and high dependency ahead of framework selection."""
    master_prompt = runtime_skill_path("master-prompt").read_text(encoding="utf-8")
    step_one = master_prompt.split("### Step 1", 1)[1].split("### Step 2", 1)[0]
    assert "immediate crisis" in step_one.lower()
    assert "high-dependency evidence" in step_one.lower()
    assert "bypass Steps 2–5" in step_one
    assert "Elevated-risk crisis is not a Phase 1 override" in step_one

    orchestration = runtime_skill_path("orchestration").read_text(encoding="utf-8")
    sanctuary_row = next(
        line for line in orchestration.splitlines() if line.startswith("| Sanctuary |")
    )
    assert "initial acute-grief period" in sanctuary_row
    assert "signals readiness" in sanctuary_row
    assert "at most one question" in sanctuary_row
    assert "2-4 sentences" not in sanctuary_row
