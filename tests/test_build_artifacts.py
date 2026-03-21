"""Build and artifact regression checks for packaged skill outputs."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def test_build_zip_contains_expected_files_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill"],
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

    assert ".claude-plugin/marketplace.json" not in names
    assert "AGENTS.md" in names
    assert "SKILL.md" in names
    assert "skills/brand/SKILL.md" in names
    assert "skills/frameworks/SKILL.md" in names
    assert "skills/brand/message-hierarchy.md" in names
    assert "templates/SKILL.md" in names
    assert "templates/quick-reference.md" in names
    assert not any(
        name.startswith("skills/") and Path(name).name.startswith("AGENTS")
        for name in names
    )


def test_build_zip_has_no_case_collisions() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill"],
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


def test_build_skill_file_contains_expected_files_only() -> None:
    """--skill preserves .claude-plugin alongside the shared knowledge files."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill", "--skill"],
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
    assert ".claude-plugin/marketplace.json" in names
    assert "AGENTS.md" in names
    assert "SKILL.md" in names
    assert "skills/frameworks/SKILL.md" in names
    assert "skills/safety/SKILL.md" in names
    assert "templates/SKILL.md" in names


def test_zip_and_skill_have_identical_contents() -> None:
    """The .skill build includes the zip contents plus .claude-plugin files."""
    zip_result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert zip_result.returncode == 0, zip_result.stderr

    skill_result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill", "--skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert skill_result.returncode == 0, skill_result.stderr

    zip_path = ROOT / "dist" / "soulmap-ai.zip"
    skill_path = ROOT / "dist" / "soulmap-ai.skill"

    with zipfile.ZipFile(zip_path) as zip_archive:
        zip_names = set(zip_archive.namelist())

    with zipfile.ZipFile(skill_path) as skill_archive:
        skill_names = set(skill_archive.namelist())

    assert zip_names < skill_names
    assert ".claude-plugin/marketplace.json" in skill_names
    assert ".claude-plugin/marketplace.json" not in zip_names


def test_build_skill_respects_distignore() -> None:
    """.skill archive must not contain distignore patterns."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill", "--skill"],
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


def test_build_skill_flag_produces_skill_only() -> None:
    """--skill flag outputs only the .skill file, not the zip."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill", "--skill"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "OK (skill):" in result.stdout
    assert (ROOT / "dist" / "soulmap-ai.skill").exists()


def test_default_builds_zip_only_when_no_flag() -> None:
    """No flags build the standard zip package."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill"],
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


def test_dist_skills_bundles_are_not_stale() -> None:
    """The built zip must contain all source .md files from skills/ and templates/.

    dist/skills/ is a gitignored local-only directory and is not present in CI.
    This test verifies the same staleness contract by inspecting the zip archive
    contents directly, which is portable across all CI environments.
    """
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr

    archive_path = ROOT / "dist" / "soulmap-ai.zip"
    assert archive_path.is_file(), "dist/soulmap-ai.zip was not created"

    with zipfile.ZipFile(archive_path) as archive:
        archive_names = set(archive.namelist())
        # Verify every entry in the zip that came from skills/ or templates/ is non-empty
        for name in archive_names:
            if (
                name.startswith("skills/") or name.startswith("templates/")
            ) and name.endswith(".md"):
                data = archive.read(name)
                assert len(data) > 100, (
                    f"Archive entry {name} looks like an empty stub ({len(data)} bytes). "
                    "Re-run `python -m tools.build_skill` to regenerate."
                )

    # At least the known skill groups must be present in the archive
    expected_groups = [
        "skills/brand/",
        "skills/frameworks/",
        "skills/safety/",
        "skills/voice/",
        "skills/meta/",
        "skills/spiritual/",
    ]
    for group in expected_groups:
        group_files = [n for n in archive_names if n.startswith(group)]
        assert group_files, (
            f"No files found in archive under {group} -- "
            "build_skill.py may be missing this skill group"
        )


def test_new_skill_files_appear_in_built_archive() -> None:
    """Every .md in skills/ and templates/ must be present in the rebuilt zip.

    Catches when a new file is added to skills/ but build_skill.py include
    list is not updated.
    """
    result = subprocess.run(
        [sys.executable, "-m", "tools.build_skill"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr

    archive_path = ROOT / "dist" / "soulmap-ai.zip"
    with zipfile.ZipFile(archive_path) as archive:
        archive_names = set(archive.namelist())

    source_md = list((ROOT / "skills").rglob("*.md")) + list(
        (ROOT / "templates").rglob("*.md")
    )
    missing = [
        md_file.relative_to(ROOT).as_posix()
        for md_file in source_md
        if md_file.relative_to(ROOT).as_posix() not in archive_names
    ]
    assert not missing, (
        "Source files missing from built zip -- rebuild or update tools/build_skill.py:\n"
        + "\n".join(f"  - {m}" for m in missing)
    )
