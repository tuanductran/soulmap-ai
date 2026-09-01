from __future__ import annotations

import io
import json
import time
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


# SOULMAP.md length rules, enforced as ceilings. The emotional-versus-
# intellectual split inside Mirror mode is a content judgment the deterministic
# layer cannot make, so Mirror is held to the higher doctrine bound.
def test_canonical_crisis_response_with_resources_is_not_flagged() -> None:
    """The correct crisis response must pass, resource block and all.

    Doctrine's "1-2 sentences" counts SoulMap's own prose, while the same rule
    requires the helpline block to come first. Counting those listings as
    sentences would flag the one response the product most needs to get right,
    so this is the load-bearing near miss for the ceiling check.
    """
    response = (
        "Please reach out right now, you deserve support. "
        "Vietnam: HOPE 0865 044 400. US: 988. UK: Samaritans 116 123. "
        "AU: Lifeline 13 11 14. International: findahelpline.com."
    )
    result = response_contract.grade_response_contract(
        response, {"primary_framework": "CRISIS", "mode": "CRISIS"}
    )

    assert result["ok"] is True


@pytest.mark.parametrize(
    ("fragment", "is_resource"),
    [
        ("988", True),
        ("0865 044 400", True),
        ("13 11 14", True),
        ("Samaritans 116 123", True),
        ("", False),
        ("That sounds heavy to carry", False),
        ("12", False),
        ("I have 2 things to say, maybe 3", False),
        # `\d` rejects the superscript two, so this stays prose. `str.isdigit()`
        # accepts it and would wrongly drop the fragment from the count.
        ("²²²", False),
    ],
    ids=[
        "us-line",
        "vietnam-line",
        "au-line",
        "uk-named-line",
        "empty",
        "prose",
        "two-digits",
        "prose-with-scattered-digits",
        "superscript-is-not-a-digit",
    ],
)
def test_resource_fragment_detection_means_three_or_more_digits(
    fragment: str, is_resource: bool
) -> None:
    """Pins the predicate that keeps the crisis resource block uncounted.

    The helper replaced a backtracking regex, so this states the contract it
    has to preserve rather than trusting the two to look equivalent.
    """
    assert response_contract._is_resource_fragment(fragment) is is_resource


def test_resource_fragment_detection_stays_linear_on_pathological_input() -> None:
    r"""A long run of non-digits must not cause catastrophic backtracking.

    The original `(?:\D*\d){3}` took roughly 2.9 seconds on 20,000 characters
    and 45 seconds on 80,000, since the nested quantifier retried every split
    point. This path runs on generated response text and on whatever the
    module's `main()` reads from stdin, so that was a denial-of-service route.
    The bound below is thousands of times slower than the current
    implementation and far faster than the old one, so it fails on a
    reintroduced backtracking pattern without being timing-sensitive.
    """
    started = time.perf_counter()
    assert response_contract._is_resource_fragment("a" * 200_000) is False
    assert time.perf_counter() - started < 2.0


def test_crisis_response_with_too_much_prose_exceeds_the_ceiling() -> None:
    response = (
        "I hear how much pain you are in. That sounds unbearable. "
        "I want you to know you matter. Please contact 988."
    )
    result = response_contract.grade_response_contract(
        response, {"primary_framework": "CRISIS", "mode": "CRISIS"}
    )

    assert "exceeds_sentence_ceiling" in cast(list[str], result["violations"])


@pytest.mark.parametrize(
    ("response", "expected_ok"),
    [
        (
            (
                "That is a real loss. You do not have to carry it neatly. "
                "Nothing needs solving tonight. I am here."
            ),
            True,
        ),
        (
            (
                "That is a real loss. You do not have to carry it neatly. "
                "Nothing needs solving tonight. I am here. Take your time."
            ),
            False,
        ),
    ],
    ids=["four-sentences-at-ceiling", "five-sentences-over-ceiling"],
)
def test_sanctuary_holds_the_four_sentence_ceiling(
    response: str, expected_ok: bool
) -> None:
    result = response_contract.grade_response_contract(
        response, {"primary_framework": "GRIEF", "mode": "SANCTUARY"}
    )

    assert result["ok"] is expected_ok


@pytest.mark.parametrize(
    ("response", "expected_ok"),
    [
        ("One.\n\nTwo.\n\nThree.\n\nWhat feels most alive in that?", True),
        ("One.\n\nTwo.\n\nThree.\n\nFour.\n\nWhat feels most alive in that?", False),
    ],
    ids=["four-paragraphs-at-ceiling", "five-paragraphs-over-ceiling"],
)
def test_mirror_holds_the_four_paragraph_ceiling(
    response: str, expected_ok: bool
) -> None:
    result = response_contract.grade_response_contract(
        response, {"primary_framework": "MIRROR", "mode": "MIRROR"}
    )

    assert result["ok"] is expected_ok


def test_mirror_ceiling_counts_paragraphs_not_length() -> None:
    """A long single paragraph is not a ceiling violation.

    Doctrine bounds paragraph count, not word count, and inventing a word limit
    here would enforce a rule SOULMAP.md does not state.
    """
    response = (
        "A long reflective paragraph that runs on and on but stays a single "
        "block, which the paragraph ceiling deliberately does not police. "
        "What sits underneath that?"
    )
    result = response_contract.grade_response_contract(
        response, {"primary_framework": "MIRROR", "mode": "MIRROR"}
    )

    assert result["ok"] is True
