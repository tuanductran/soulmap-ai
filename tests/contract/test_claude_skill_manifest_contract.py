"""Validate the shipped Claude Skill discovery metadata contract."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MANIFEST = REPO_ROOT / "SKILL.md"

_FRONTMATTER_RE = re.compile(
    r"\A---\r?\n(?P<header>.*?)\r?\n---(?:\r?\n|$)",
    re.DOTALL,
)
_SCALAR_RE_TEMPLATE = r"""^{key}:\s*(?:"([^"]*)"|'([^']*)'|([^\r\n#]+?))\s*(?:#.*)?$"""
_NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_RESERVED_NAME_PARTS = {"anthropic", "claude"}


def _frontmatter(content: str) -> str:
    """Return opening YAML front matter, rejecting absent or non-leading metadata."""
    match = _FRONTMATTER_RE.match(content)
    assert match is not None, "SKILL.md must start with YAML front matter"
    return match.group("header")


def _scalar(header: str, key: str) -> str | None:
    """Read a simple single-line scalar from the Skill front matter."""
    pattern = re.compile(_SCALAR_RE_TEMPLATE.format(key=re.escape(key)), re.MULTILINE)
    match = pattern.search(header)
    if match is None:
        return None
    return next((value for value in match.groups() if value is not None), "").strip()


def test_shipped_skill_has_valid_claude_discovery_metadata() -> None:
    """Claude needs valid name/description metadata to discover the shipped Skill."""
    header = _frontmatter(SKILL_MANIFEST.read_text(encoding="utf-8"))
    name = _scalar(header, "name")
    description = _scalar(header, "description")

    assert name, "SKILL.md front matter must declare a non-empty name"
    assert len(name) <= 64, "Skill name must be at most 64 characters"
    assert _NAME_RE.fullmatch(name), (
        "Skill name must use lowercase letters, digits, and single hyphen separators"
    )
    assert not (_RESERVED_NAME_PARTS & set(name.split("-"))), (
        "Skill name must not contain reserved Anthropic/Claude name parts"
    )

    assert description, "SKILL.md front matter must declare a non-empty description"
    assert len(description) <= 1024, "Skill description must be at most 1024 characters"
    assert "<" not in description and ">" not in description, (
        "Skill description must not contain XML/HTML tag delimiters"
    )
