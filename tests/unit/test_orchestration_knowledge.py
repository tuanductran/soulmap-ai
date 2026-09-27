from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules
from soulmap.runtime.knowledge.template_source import (
    load_template_rules,
    resolve_template,
)


def test_orchestration_contract_loads_complete_priority_and_overrides() -> None:
    rules = load_orchestration_rules()

    assert rules.priority[0] == "Crisis"
    assert rules.priority[-1] == "Mirror"
    assert rules.secondary_layers == (
        "anger",
        "bypass",
        "somatic",
        "meaning_integration",
        "inner_parts",
    )
    assert rules.stage1_stage == 1
    assert rules.stage1_max_user_turn == 2
    assert rules.stage1_framework == "Mirror"
    assert rules.breakthrough_framework == "Meaning Integration"


def test_template_contract_resolves_stage_one_and_grief_variants() -> None:
    rules = load_template_rules()

    assert resolve_template("MIRROR", "MIRROR", {"stage": 1}).framework == "Mirror (Stage 1)"
    assert (
        resolve_template(
            "GRIEF",
            "SANCTUARY",
            {"grief": {"grief_type": "acute"}},
        ).framework
        == "Grief (acute)"
    )
    assert len(rules) >= 30
