"""Verify the orchestration Markdown exposes valid executable routing values."""

from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules


def test_orchestration_runtime_contract_loads() -> None:
    rules = load_orchestration_rules()

    assert rules.stage_1_max_user_messages == 2
    assert rules.breakthrough_min_strength == "strong"
    assert rules.phase_1_safety_before_framework_selection is True
    assert rules.template_routing_required is True
    assert rules.peer_min_stage == 5
    assert [(rule.level, rule.framework, rule.mode) for rule in rules.intensity_fallback] == [
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
