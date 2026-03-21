"""Ensure SKILL.md inventories match shipped skill files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
TEMPLATES_DIR = ROOT / "templates"


def _extract_files_listed(skill_md: Path) -> set[str]:
    content = skill_md.read_text(encoding="utf-8")
    in_section = False
    listed: set[str] = set()
    for line in content.splitlines():
        if line.strip() == "## Files in this skill":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- `") and line.strip().endswith("`"):
            entry = line.strip()[3:-1]
            listed.add(entry)
    return listed


def _actual_skill_files(group_dir: Path) -> set[str]:
    return {p.name for p in group_dir.glob("*.md") if p.name != "SKILL.md"}


def test_each_skill_list_matches_directory() -> None:
    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        if skill_md.parent == SKILLS_DIR:
            # Root SKILL.md is a high-level entry point, not a file inventory.
            continue
        listed = _extract_files_listed(skill_md)
        actual = _actual_skill_files(skill_md.parent)
        assert listed, f"{skill_md}: missing 'Files in this skill' entries"
        assert actual == listed, (
            f"{skill_md} mismatch.\n"
            f"Missing from SKILL.md: {sorted(actual - listed)}\n"
            f"Extra in SKILL.md: {sorted(listed - actual)}"
        )


def test_templates_skill_list_matches_directory() -> None:
    skill_md = TEMPLATES_DIR / "SKILL.md"
    listed = _extract_files_listed(skill_md)
    actual = {p.name for p in TEMPLATES_DIR.glob("*.md") if p.name != "SKILL.md"}
    assert listed, f"{skill_md}: missing 'Files in this skill' entries"
    assert actual == listed, (
        f"{skill_md} mismatch.\n"
        f"Missing from SKILL.md: {sorted(actual - listed)}\n"
        f"Extra in SKILL.md: {sorted(listed - actual)}"
    )
