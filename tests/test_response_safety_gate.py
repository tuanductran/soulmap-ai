from __future__ import annotations

from typing import cast

from modules.resource_sanitizer import check_banned_language
from modules.response_contract import grade_response_contract
from modules.response_safety_gate import apply_safety_gate


def test_safety_gate_overrides_crisis() -> None:
    result = apply_safety_gate(
        "I want to hurt myself.",
        [{"role": "user", "content": "I want to hurt myself."}],
        {},
        {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )
    assert result["status"] == "OVERRIDE"
    selection = cast(dict[str, object], result["selection"])
    assert selection["primary_framework"] == "CRISIS"


def test_response_contract_accepts_single_closing_question() -> None:
    grade = grade_response_contract(
        "That feeling sounds real. Sometimes the hardest part is staying close to what hurts without rushing away from it. What feels most alive in you right now?",
        {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )
    assert grade["ok"] is True


def test_response_contract_rejects_multiple_questions() -> None:
    grade = grade_response_contract(
        "That feeling sounds real. What feels most alive in you right now? What needs care first?",
        {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )
    assert grade["ok"] is False
    violations = cast(list[str], grade["violations"])
    assert "multiple_questions" in violations


def test_resource_sanitizer_rejects_dependency_inviting_closing() -> None:
    result = check_banned_language(
        "That clarity matters. Come back anytime if you need me again."
    )
    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    violations = cast(list[str], result["violations"])
    assert any("come back anytime" in item for item in violations)
