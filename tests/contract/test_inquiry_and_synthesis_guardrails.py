"""Protect low-assumption inquiry and user-led longitudinal synthesis rules."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_skill(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return " ".join(text.split())


def test_cross_session_synthesis_requires_explicit_user_intent_and_host_context() -> None:
    """Prevent context availability from becoming unsolicited longitudinal analysis."""
    content = _normalize(_read_skill("skills/frameworks/conversation-synthesis.md"))

    assert (
        "Compare across sessions only when the user explicitly requests it" in content
    )
    assert "Context availability alone is not" in content
    assert "permission to initiate a longitudinal reading" in content
    assert "Explicit cross-session request signals" in content
    assert "General requests to reflect on the current conversation do not count." in content
    assert "compare this with our previous sessions" in content


def test_cross_pattern_questions_preserve_uncertainty_and_user_authority() -> None:
    """Keep cross-pattern questions tentative rather than imposing a shared cause."""
    content = _read_skill("skills/meta/deep-inquiry-bank.md")
    section = content.split(
        "### Cross-Pattern (when combination detected)", maxsplit=1
    )[1]
    section = section.split("\n## ", maxsplit=1)[0]
    section = _normalize(section)

    assert (
        "If you look across these situations, what recurring response, if any, do you notice?"
        in section
    )
    assert (
        "Do you notice a common thread across these stories, or do they feel separate to you?"
        in section
    )
    assert (
        "What, if anything, seems to influence whether this cycle repeats or changes?"
        in section
    )


def test_inquiry_is_single_question_and_does_not_assume_origin_or_motive() -> None:
    """Keep inquiry bounded by readiness, evidence, and conscious silence."""
    content = _normalize(_read_skill("skills/meta/deep-inquiry-bank.md"))

    assert "Only one question per turn" in content
    assert "No assumed origin or motive" in content
    assert "Explore history only when the user has introduced it" in content
    assert "Present before past" in content
    assert "Conscious silence" in content
