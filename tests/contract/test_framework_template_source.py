"""Verify runtime template routing stays aligned with the Markdown map."""

from soulmap.runtime.knowledge.framework_template_source import (
    load_template_rules,
    resolve_template,
)


def test_template_contract_resolves_crisis() -> None:
    template = resolve_template("CRISIS", "CRISIS")
    assert template["name"] == "Crisis"
    assert template["question_rule"] == "None, resources only"


def test_template_contract_resolves_stage_one_mirror() -> None:
    template = resolve_template(
        "MIRROR",
        "MIRROR",
        {"stage_override": True},
    )
    assert template["name"] == "Mirror (Stage 1)"
    assert template["source_file"] == "response-structure.md"


def test_template_contract_resolves_moderate_de_escalation() -> None:
    template = resolve_template("DE_ESCALATION", "MIRROR")
    assert template["name"] == "De-escalation (MODERATE)"


def test_template_contract_declares_unique_runtime_framework_variants() -> None:
    rules = load_template_rules()
    keys = {(rule.runtime_framework, rule.runtime_variant) for rule in rules}

    assert len(rules) == len(keys)
    assert ("INTEGRATION_CELEBRATION", "default") in keys
    assert ("MIRROR", "stage_1") in keys
    assert ("GRIEF", "acute") in keys
