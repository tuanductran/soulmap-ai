"""Verify runtime template routing stays aligned with the Markdown map."""

from soulmap.runtime.knowledge.framework_template_source import resolve_template


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
