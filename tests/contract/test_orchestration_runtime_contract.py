"""Verify the orchestration Markdown exposes valid executable routing values."""

from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path


def test_orchestration_runtime_contract_loads() -> None:
    rules = load_orchestration_rules()

    assert rules.stage_1_max_user_messages == 2
    assert rules.breakthrough_min_strength == "strong"
    assert rules.phase_1_safety_before_framework_selection is True
    assert rules.template_routing_required is True
    assert rules.peer_min_stage == 5
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
        "Stage 1 override": "Stage 1 first-contact override. Use minimal-depth presence and reflection; do not activate a framework.",
        "HIGH intensity": "Sanctuary mode. Acknowledge, ground, and normalize. Do not use a five-step framework or ask an inquiry question. Keep the response to 2-4 sentences.",
        "MODERATE intensity": "Hold the framework lightly and slow the conversation before deeper reflection.",
        "MIRROR fallback": "Use the response-structure arc and, when appropriate, end with at most one question from deep-inquiry-bank.md. Respect mode, safety, and user readiness; zero questions is valid when a question would add pressure.",
        "PEER fallback": "Use dialogue and light structure, with at most one question when it supports the conversation. Do not force a question merely to satisfy the format.",
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
    text = runtime_skill_path("orchestration").read_text(encoding="utf-8")
    policy = text.split("## Routing policy", 1)[1].split("## Decision Tree", 1)[0]

    for token in ("DE_ESCALATION", "INNER_PARTS", "meaning_integration", "inner_parts"):
        assert token not in policy
    assert "| High | De-escalation | Sanctuary |" in policy
    assert "| 1 | Grief | Sanctuary |" in policy
