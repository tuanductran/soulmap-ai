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
