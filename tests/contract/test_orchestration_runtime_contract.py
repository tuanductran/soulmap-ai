"""Verify the orchestration Markdown exposes valid executable routing values."""

from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules


def test_orchestration_runtime_contract_loads() -> None:
    rules = load_orchestration_rules()
    assert rules.stage_1_max_user_messages == 2
    assert rules.breakthrough_min_strength == "strong"
    assert rules.phase_1_safety_before_framework_selection is True
    assert rules.template_routing_required is True
