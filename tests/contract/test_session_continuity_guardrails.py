"""Protect host-provided context boundaries and session continuity behavior."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _normalized_skill(relative_path: str) -> str:
    content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    return " ".join(content.split())


def test_session_continuity_uses_only_host_supplied_context() -> None:
    """Prevent fabricated memory or claims of independently retained history."""
    content = _normalized_skill("skills/meta/session-continuity.md")

    assert "SoulMap does not independently store or retrieve a user's conversation history." in content
    assert "A host platform may supply a summary, selected facts, or other prior-session context" in content
    assert "Context availability alone is not permission to initiate a longitudinal reading." in content
    assert "Do not promise that SoulMap will retain or recall information in a future session." in content
    assert "Do not say \"I remember\"" in content


def test_returning_session_opening_remains_user_led() -> None:
    """Prevent unsolicited resurfacing of prior-session details."""
    content = _normalized_skill("skills/voice/session-rituals.md")

    assert "Do not summarize what was discussed before." in content
    assert "Use surfaced context only when the user explicitly asks to continue or makes the connection themselves." in content
    assert "Do not surface a prior-session insight merely because the current topic resembles it." in content
