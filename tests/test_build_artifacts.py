"""Build and artifact regression checks for packaged skill outputs."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def test_build_skill_zip_contains_expected_files_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr

    archive_path = ROOT / "dist" / "soulmap-ai.zip"
    assert archive_path.is_file()

    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())

    assert ".claude-plugin/marketplace.json" in names
    assert "skills/brand/SKILL.md" in names
    assert "skills/frameworks/SKILL.md" in names
    assert "skills/brand/message-hierarchy.md" in names
    assert "templates/SKILL.md" in names
    assert "templates/quick-reference.md" in names
    assert "SKILL.md" not in names
    assert not any(
        name.startswith("skills/") and Path(name).name.startswith("AGENTS")
        for name in names
    )


def test_build_skill_zip_has_no_case_collisions() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr

    archive_path = ROOT / "dist" / "soulmap-ai.zip"
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

    seen: dict[str, str] = {}
    collisions: list[tuple[str, str]] = []
    for name in names:
        key = name.lower()
        if key in seen and seen[key] != name:
            collisions.append((seen[key], name))
        else:
            seen[key] = name

    assert collisions == []


def test_build_skill_file_has_root_skill_md() -> None:
    """--skill produces a .skill archive with a root-level SKILL.md manifest."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip", "--skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr

    skill_path = ROOT / "dist" / "soulmap-ai.skill"
    assert skill_path.is_file(), "soulmap-ai.skill was not created"

    with zipfile.ZipFile(skill_path) as archive:
        names = set(archive.namelist())
        # Root-level SKILL.md must be present (Agent Skills spec requirement)
        assert "SKILL.md" in names, "Root SKILL.md missing from .skill archive"
        # AGENTS.md should be included for full behavioral contract
        assert "AGENTS.md" in names, "AGENTS.md missing from .skill archive"
        # All skill groups must be present
        assert "skills/frameworks/SKILL.md" in names
        assert "skills/safety/SKILL.md" in names
        assert "templates/SKILL.md" in names


def test_build_skill_root_skill_md_has_valid_frontmatter() -> None:
    """Root SKILL.md in .skill archive must have name + description frontmatter."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip", "--skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr

    skill_path = ROOT / "dist" / "soulmap-ai.skill"
    with zipfile.ZipFile(skill_path) as archive:
        content = archive.read("SKILL.md").decode("utf-8")

    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert "name:" in content, "SKILL.md frontmatter must include name"
    assert "description:" in content, "SKILL.md frontmatter must include description"
    assert "soulmap-ai" in content, "SKILL.md name must be soulmap-ai"


def test_build_skill_respects_distignore() -> None:
    """.skill archive must not contain distignore patterns."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip", "--skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr

    skill_path = ROOT / "dist" / "soulmap-ai.skill"
    with zipfile.ZipFile(skill_path) as archive:
        names = archive.namelist()

    banned = [".DS_Store", "Icon?", "/._"]
    for name in names:
        for pattern in banned:
            assert pattern not in name, (
                f"distignore pattern '{pattern}' found in .skill: {name}"
            )


def test_build_zip_flag_produces_zip_only() -> None:
    """--zip flag outputs only the zip, not .skill."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip", "--zip"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "OK (zip):" in result.stdout
    assert "OK (skill):" not in result.stdout
    assert (ROOT / "dist" / "soulmap-ai.zip").exists()


def test_build_skill_flag_produces_skill_only() -> None:
    """--skill flag outputs only the .skill file, not the zip."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip", "--skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "OK (skill):" in result.stdout
    assert "OK (zip):" not in result.stdout
    assert (ROOT / "dist" / "soulmap-ai.skill").exists()


def test_build_all_flag_produces_both() -> None:
    """--all flag outputs both zip and .skill."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip", "--all"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "OK (zip):" in result.stdout
    assert "OK (skill):" in result.stdout
    assert (ROOT / "dist" / "soulmap-ai.zip").exists()
    assert (ROOT / "dist" / "soulmap-ai.skill").exists()


def test_default_builds_zip_only_when_no_flag() -> None:
    """No flags = same as --zip (backward compatible)."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill_zip"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "OK (zip):" in result.stdout
    assert "OK (skill):" not in result.stdout
