"""Contract checks for skill and template metadata."""

from __future__ import annotations

import json
from pathlib import Path


def _read_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return frontmatter
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return {}


def test_skill_and_template_names_match_filename_stems() -> None:
    for folder in [Path("skills"), Path("templates")]:
        for path in sorted(folder.rglob("*.md")):
            frontmatter = _read_frontmatter(path)
            name = frontmatter.get("name")
            expected_name = path.parent.name if path.name == "SKILL.md" else path.stem
            assert name == expected_name, (
                f"{path} frontmatter name must equal {expected_name}"
            )


def test_claude_plugin_marketplace_exists_and_points_to_repo_assets() -> None:
    path = Path(".claude-plugin/marketplace.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["name"] == "soulmap-ai"
    assert isinstance(data["description"], str)
    plugins = {plugin["name"]: plugin for plugin in data["plugins"]}
    assert plugins["SoulMap Brand System"]["skills"] == ["./skills/brand"]
    assert plugins["SoulMap Templates Library"]["skills"] == ["./templates"]


def test_skill_markdown_contract() -> None:
    paths = [
        Path("skills/brand/SKILL.md"),
        Path("skills/frameworks/SKILL.md"),
        Path("skills/meta/SKILL.md"),
        Path("skills/safety/SKILL.md"),
        Path("skills/spiritual/SKILL.md"),
        Path("skills/voice/SKILL.md"),
        Path("templates/SKILL.md"),
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        frontmatter = _read_frontmatter(path)
        assert frontmatter.get("description")
        assert frontmatter.get("license") == "Complete terms in LICENSE"
        assert "## Use this skill when" in content
        assert "## Workflow" in content
        assert "## Files in this skill" in content
        assert "## Expected outcome" in content
