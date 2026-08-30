from __future__ import annotations

import io
import json
from typing import cast

import pytest

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


def test_response_contract_cli_returns_serialized_grade(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
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


def test_resource_sanitizer_cli_returns_serialized_check(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        resource_sanitizer.sys,
        "stdin",
        io.StringIO(json.dumps({"response_text": "A clean reflection."})),
    )

    assert resource_sanitizer.main() == 0
    assert json.loads(capsys.readouterr().out) == {"status": "PASS", "violations": []}


# --- Question-rule edge cases for sanctuary and crisis modes ---
#
# The safety-enforcement matrix flagged these two modes as needing more edge
# cases than the single "a question is rejected" case above. Crisis and
# sanctuary are the two modes where the response must hold rather than ask, so
# both a missed violation and a false one carry a cost: a missed one lets a
# crisis reply end in a question, and a false one sends a valid crisis reply
# back for a rewrite it does not need.

_CRISIS: dict[str, object] = {"primary_framework": "CRISIS", "mode": "CRISIS"}
_SANCTUARY: dict[str, object] = {"primary_framework": "MIRROR", "mode": "SANCTUARY"}
_MIRROR: dict[str, object] = {"primary_framework": "MIRROR", "mode": "MIRROR"}
_CRISIS_MIRROR_MODE: dict[str, object] = {
    "primary_framework": "CRISIS",
    "mode": "MIRROR",
}


def test_crisis_response_with_resource_link_query_string_is_not_a_question() -> None:
    """A question mark inside a link is punctuation, not a question.

    Crisis responses are exactly where links appear. SOULMAP.md names
    findahelpline.com as an international resource, and a localized link
    carries a query string. Counting that "?" flagged a valid crisis response
    as asking a question and would have sent the crisis resources back for an
    unnecessary rewrite.
    """
    result = response_contract.grade_response_contract(
        "Please reach out now. findahelpline.com/?country=vn", _CRISIS
    )

    assert result == {"ok": True, "violations": []}


def test_a_real_question_still_counts_when_a_link_is_present() -> None:
    """Only the link's own punctuation is excluded, not the whole response."""
    result = response_contract.grade_response_contract(
        "What feels true? Then visit findahelpline.com/?c=vn", _MIRROR
    )

    assert result == {"ok": False, "violations": ["question_not_last"]}


def test_crisis_response_without_a_question_passes() -> None:
    result = response_contract.grade_response_contract(
        "Please reach the Samaritans at 116 123 right now.", _CRISIS
    )

    assert result == {"ok": True, "violations": []}


def test_sanctuary_response_without_a_question_passes() -> None:
    result = response_contract.grade_response_contract(
        "You do not have to carry this alone.", _SANCTUARY
    )

    assert result == {"ok": True, "violations": []}


def test_multiple_questions_in_crisis_report_both_violations() -> None:
    """The mode rule and the count rule are independent checks.

    Reporting only one would hide half of what needs fixing.
    """
    result = response_contract.grade_response_contract(
        "Are you safe? Can you call someone?", _CRISIS
    )

    assert result["ok"] is False
    violations = result["violations"]
    assert isinstance(violations, list)
    assert set(violations) == {"multiple_questions", "crisis_no_question"}


def test_crisis_mode_flag_applies_regardless_of_the_mode_field() -> None:
    """The crisis rule keys off the primary framework, not the mode label.

    A crisis route carries mode CRISIS in normal operation, but the rule must
    not depend on the two agreeing.
    """
    result = response_contract.grade_response_contract(
        "Are you safe right now?", _CRISIS_MIRROR_MODE
    )

    assert result == {"ok": False, "violations": ["crisis_no_question"]}
