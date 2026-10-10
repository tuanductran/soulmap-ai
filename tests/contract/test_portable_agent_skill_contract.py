from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_skill_instructions_are_provider_neutral() -> None:
    content = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "not independent Skills" in content
    assert "Claude" not in content
    assert "Anthropic" not in content
    assert ".claude/" not in content


def test_openai_skills_api_guide_separates_static_review_from_live_acceptance() -> None:
    guide = (REPO_ROOT / "docs" / "integrations" / "openai-skills-api.md").read_text(
        encoding="utf-8"
    )

    required = (
        "dist/soulmap-ai-claude.zip",
        "single top-level",
        "OPENAI_API_KEY",
        "https://api.openai.com/v1/skills",
        "live API acceptance remains unverified",
        "Issue #617",
        "must never be committed or added to CI",
    )
    missing = [anchor for anchor in required if anchor not in guide]
    assert not missing, (
        f"openai-skills-api.md is missing contract anchors: {missing}"
    )
