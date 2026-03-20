"""Trigger and boundary validation for local .claude/skills/."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_SKILLS_DIR = ROOT / ".claude" / "skills"
SHIPPED_SKILLS_DIR = ROOT / "skills"
TEMPLATES_DIR = ROOT / "templates"


def _read_skill(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return {}


def _iter_local_skill_files() -> list[Path]:
    return sorted(
        path
        for path in CLAUDE_SKILLS_DIR.rglob("SKILL.md")
        if path.parent != CLAUDE_SKILLS_DIR
    )


# ---------------------------------------------------------------------------
# Issue 1 fix: README clearly distinguishes local vs shipped knowledge
# ---------------------------------------------------------------------------


def test_readme_mentions_shipped_skills_distinction() -> None:
    readme = (CLAUDE_SKILLS_DIR / "README.md").read_text(encoding="utf-8")
    assert "repo-workflow tools only" in readme, (
        "README must state that .claude/skills/ contains repo-workflow tools only"
    )
    assert "skills/" in readme, "README must reference the shipped skills/ directory"
    assert "templates/" in readme, (
        "README must reference the shipped templates/ directory"
    )


def test_readme_links_to_shipped_knowledge_locations() -> None:
    readme = (CLAUDE_SKILLS_DIR / "README.md").read_text(encoding="utf-8")
    expected_sections = [
        "skills/frameworks/",
        "skills/safety/",
        "skills/brand/",
        "templates/",
        "AGENTS.md",
    ]
    for section in expected_sections:
        assert section in readme, (
            f"README should reference shipped knowledge path: {section}"
        )


# ---------------------------------------------------------------------------
# Issue 3 fix: skill descriptions contain meaningful trigger language
# ---------------------------------------------------------------------------


def test_skill_descriptions_are_non_trivial() -> None:
    """Each skill description must be long enough to be a real trigger phrase."""
    for path in _iter_local_skill_files():
        fm = _read_frontmatter(path)
        description = fm.get("description", "")
        assert len(description) >= 40, (
            f"{path}: description is too short to be meaningful ({len(description)} chars): "
            f"'{description}'"
        )


def test_skill_descriptions_contain_action_verbs() -> None:
    """Descriptions should start with an action verb (Review, Write, Analyze, etc.)."""
    action_verbs = {
        "review",
        "write",
        "update",
        "analyze",
        "analyse",
        "design",
        "add",
        "create",
        "check",
        "build",
        "draft",
        "maintain",
    }
    for path in _iter_local_skill_files():
        fm = _read_frontmatter(path)
        description = fm.get("description", "").lower()
        # Strip trailing punctuation e.g. "Add," -> "add"
        first_word = description.split()[0].rstrip(",.;:") if description else ""
        assert first_word in action_verbs, (
            f"{path}: description should start with an action verb. "
            f"Got '{first_word}' in: '{fm.get('description', '')}'"
        )


def test_each_skill_has_distinct_description() -> None:
    """No two skills should have identical descriptions."""
    descriptions: dict[str, Path] = {}
    for path in _iter_local_skill_files():
        fm = _read_frontmatter(path)
        desc = fm.get("description", "").strip()
        assert desc not in descriptions, (
            f"Duplicate description found:\n"
            f"  {descriptions[desc]}\n"
            f"  {path}\n"
            f"  description: '{desc}'"
        )
        descriptions[desc] = path


def test_skill_use_cases_do_not_implement_runtime_behavior() -> None:
    """
    Local .claude/skills/ must not EXECUTE SoulMap runtime actions.
    Referencing these concepts for review or audit purposes is fine.
    Only flag phrases that would appear if the skill itself runs the action.
    """
    implementation_phrases = [
        "select the framework",
        "run the crisis detector",
        "apply the safety gate",
        "call detect_crisis",
        "call analyze_dependency",
        "return primary_framework",
    ]
    for path in _iter_local_skill_files():
        content = _read_skill(path).lower()
        for phrase in implementation_phrases:
            assert phrase not in content, (
                f"{path}: local skill must not execute SoulMap runtime behavior. "
                f"Found: '{phrase}'. Runtime execution belongs in modules/."
            )


def test_skill_do_not_use_sections_are_present() -> None:
    """Every skill must declare what it should NOT be used for."""
    for path in _iter_local_skill_files():
        content = _read_skill(path)
        has_do_not = (
            "Do not use this skill for" in content
            or "Do not use for" in content
            or "do not use" in content.lower()
        )
        assert has_do_not, (
            f"{path}: skill must include a 'Do not use' section to prevent misuse"
        )


def test_skill_workflow_sections_reference_agents_or_repo_files() -> None:
    """
    Workflow sections should anchor to real repo files (AGENTS.md, modules/, etc.)
    rather than operating in isolation.
    """
    repo_anchors = [
        "agents.md",
        "modules/",
        "skills/",
        "templates/",
        "docs/",
        ".claude/rules/",
    ]
    for path in _iter_local_skill_files():
        content = _read_skill(path).lower()
        has_anchor = any(anchor in content for anchor in repo_anchors)
        assert has_anchor, (
            f"{path}: workflow section should reference at least one real repo file "
            f"(AGENTS.md, modules/, skills/, templates/, docs/, .claude/rules/)"
        )


# ---------------------------------------------------------------------------
# Boundary: local skills must not duplicate shipped product knowledge files
# ---------------------------------------------------------------------------


def test_local_skills_do_not_shadow_shipped_skill_names() -> None:
    """
    .claude/skills/ directory names must not match shipped skills/ group names.
    This prevents confusion about which layer is authoritative.
    """
    shipped_groups = {
        path.name for path in SHIPPED_SKILLS_DIR.iterdir() if path.is_dir()
    }
    local_skill_dirs = {path.parent.name for path in _iter_local_skill_files()}
    overlap = local_skill_dirs & shipped_groups
    assert not overlap, (
        f"Local .claude/skills/ dirs shadow shipped skills/ group names: {overlap}. "
        "Rename local skills to avoid confusion."
    )


def test_shipped_skills_dir_exists_and_has_content() -> None:
    """Verify the shipped knowledge base is present and populated."""
    assert SHIPPED_SKILLS_DIR.is_dir(), "skills/ directory must exist"
    assert TEMPLATES_DIR.is_dir(), "templates/ directory must exist"

    skill_files = list(SHIPPED_SKILLS_DIR.rglob("*.md"))
    assert len(skill_files) >= 10, (
        f"Expected at least 10 shipped skill files, found {len(skill_files)}"
    )

    template_files = list(TEMPLATES_DIR.glob("*.md"))
    assert len(template_files) >= 5, (
        f"Expected at least 5 template files, found {len(template_files)}"
    )


def test_agents_md_is_at_repo_root() -> None:
    """AGENTS.md must exist at repo root as the primary behavioral contract."""
    agents = ROOT / "AGENTS.md"
    claude = ROOT / "CLAUDE.md"
    assert agents.is_file(), "AGENTS.md must exist at repo root"
    assert claude.is_file(), "CLAUDE.md must exist at repo root"

    agents_content = agents.read_text(encoding="utf-8")
    claude_content = claude.read_text(encoding="utf-8")

    assert "## Section 4 - Non-Negotiable Safety Rules" in agents_content, (
        "AGENTS.md must contain safety rules"
    )
    assert len(claude_content) > 500, (
        "CLAUDE.md must contain substantive content, not just a reference string"
    )


def test_agents_md_and_claude_md_are_in_sync() -> None:
    """CLAUDE.md should contain the same core safety rules as AGENTS.md."""
    agents_content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    claude_content = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    key_sections = [
        "## Section 4 - Non-Negotiable Safety Rules",
        "## Section 1 - The Mirror Principle",
        "The North Star",
    ]
    for section in key_sections:
        assert section in agents_content, f"AGENTS.md missing: {section}"
        assert section in claude_content, (
            f"CLAUDE.md is out of sync with AGENTS.md - missing: {section}"
        )


# ---------------------------------------------------------------------------
# Ensure CI contract test still covers the basics
# ---------------------------------------------------------------------------


def test_all_local_skills_listed_in_readme() -> None:
    readme = (CLAUDE_SKILLS_DIR / "README.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"^- `([a-z0-9-]+)`$", readme, flags=re.MULTILINE))
    actual = {path.parent.name for path in _iter_local_skill_files()}
    missing_from_readme = actual - listed
    assert not missing_from_readme, (
        f"Skills exist but are not listed in README: {missing_from_readme}"
    )
