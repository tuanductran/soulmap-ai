from __future__ import annotations

import io
import json
from typing import cast

from soulmap.runtime.guards import resource_sanitizer, response_contract


def test_response_contract_accepts_a_clean_single_closing_question() -> None:
    result = response_contract.grade_response_contract(
        "That feeling is worth staying close to. What feels most present right now?",
        {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )

    assert result == {"ok": True, "violations": []}


def test_response_contract_collects_standard_structure_violations() -> None:
    result = response_contract.grade_response_contract(
        "? What happened?\n- A bullet point;\nWhat remains?",
        {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )

    assert result == {
        "ok": False,
        "violations": [
            "multiple_questions",
            "starts_with_question",
            "semicolon",
            "bullets",
        ],
    }


def test_response_contract_rejects_question_that_is_not_last() -> None:
    result = response_contract.grade_response_contract(
        "What feels true now? Stay with that feeling.",
        {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )

    assert result == {"ok": False, "violations": ["question_not_last"]}


def test_response_contract_rejects_questions_in_crisis_and_sanctuary() -> None:
    crisis = response_contract.grade_response_contract(
        "Please contact local emergency support now?",
        {"primary_framework": "CRISIS", "mode": "MIRROR"},
    )
    sanctuary = response_contract.grade_response_contract(
        "You do not have to carry this alone?",
        {"primary_framework": "MIRROR", "mode": "SANCTUARY"},
    )

    assert crisis == {"ok": False, "violations": ["crisis_no_question"]}
    assert sanctuary == {"ok": False, "violations": ["sanctuary_no_question"]}


def test_response_contract_cli_returns_serialized_grade(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        response_contract.sys,
        "stdin",
        io.StringIO(
            json.dumps(
                {
                    "response": "What feels most present right now?",
                    "selection": {"primary_framework": "MIRROR", "mode": "MIRROR"},
                }
            )
        ),
    )

    assert response_contract.main() == 0
    assert json.loads(capsys.readouterr().out) == {"ok": True, "violations": []}


def test_resource_sanitizer_accepts_clean_reflective_language() -> None:
    result = resource_sanitizer.check_banned_language(
        "Something in this moment may be asking to be noticed more slowly."
    )

    assert result == {"status": "PASS", "violations": []}


def test_resource_sanitizer_rejects_all_banned_vocabulary_case_insensitively() -> None:
    result = resource_sanitizer.check_banned_language(
        "ACTION STEPS, goals, milestones, aligns with, dysregulated, nervous system, "
        "window of tolerance, and hyperarousal."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    assert result["violations"] == resource_sanitizer.BANNED_WORDS
    assert "Rewrite response" in str(result["instruction"])


def test_resource_sanitizer_rejects_dependency_and_structure_violations() -> None:
    result = resource_sanitizer.check_banned_language(
        "I am here for you; come back anytime.\n- Keep talking. What now? Why now?"
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    violations = cast(list[str], result["violations"])
    assert r"\bcome back anytime\b" in violations
    assert r"\bi(?:'| a)?m here for you\b" in violations
    assert "; (semicolons are forbidden)" in violations
    assert "bullet_points" in violations
    assert "multiple_questions" in violations


def test_resource_sanitizer_rejects_a_nonfinal_single_question() -> None:
    result = resource_sanitizer.check_banned_language(
        "What feels present? Stay with that for a moment."
    )

    assert result["status"] == "FAIL_REWRITE_REQUIRED"
    assert result["violations"] == ["question_not_last_sentence"]


def test_resource_sanitizer_cli_returns_serialized_check(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        resource_sanitizer.sys,
        "stdin",
        io.StringIO(json.dumps({"response_text": "A clean reflection."})),
    )

    assert resource_sanitizer.main() == 0
    assert json.loads(capsys.readouterr().out) == {"status": "PASS", "violations": []}
