"""Build and artifact regression checks for packaged skill outputs."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def test_package_skills_main_writes_bundle_and_source_log() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "modules.package_skills"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr

    bundle_path = ROOT / "skills" / "AGENTS.md"
    log_path = ROOT / "skills" / "AGENTS.sources.jsonl"

    assert bundle_path.is_file()
    assert log_path.is_file()
    assert "brand/brand_doctrine.md" in result.stdout

    first_entry = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    assert first_entry["path"].endswith(".md")


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

    assert "SKILL.md" in names
    assert "skills/AGENTS.md" in names
    assert "skills/brand/message_hierarchy.md" in names
    assert "templates/quick_reference.md" in names
    assert "skills/AGENTS.sources.jsonl" not in names


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
