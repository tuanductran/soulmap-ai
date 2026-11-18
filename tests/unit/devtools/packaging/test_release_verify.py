"""Tests for release artifact and integration verification contracts."""

import os
import zipfile
from pathlib import Path

import pytest

from soulmap.devtools.packaging.release_verify import (
    INTEGRATION_GUIDES,
    ReleaseVerificationError,
    _source_members,
    _verify_archive,
    _verify_integrations,
)


def _write_guides(root: Path, *, version: str = "0.11.0") -> None:
    guide_dir = root / "docs" / "integrations"
    guide_dir.mkdir(parents=True)
    front_matter = (
        f'---\ndoctrine_source: "SOULMAP.md"\nsoulmap_version: "{version}"\n---\n\n'
    )
    for relative_path in INTEGRATION_GUIDES:
        path = root / relative_path
        path.write_text(front_matter + "# Guide\n", encoding="utf-8")


def test_verify_integrations_accepts_all_supported_guides(tmp_path: Path) -> None:
    _write_guides(tmp_path)

    results = _verify_integrations(tmp_path, "0.11.0")

    assert len(results) == 4
    assert all(result["doctrine_source"] == "SOULMAP.md" for result in results)
    assert all(result["soulmap_version"] == "0.11.0" for result in results)


def test_verify_integrations_rejects_version_drift(tmp_path: Path) -> None:
    _write_guides(tmp_path, version="0.10.0")

    with pytest.raises(
        ReleaseVerificationError,
        match=r"soulmap_version must be 0\.11\.0, got 0\.10\.0",
    ):
        _verify_integrations(tmp_path, "0.11.0")


def test_verify_integrations_rejects_doctrine_source_drift(tmp_path: Path) -> None:
    _write_guides(tmp_path)
    path = tmp_path / INTEGRATION_GUIDES[0]
    path.write_text(
        path.read_text(encoding="utf-8").replace("SOULMAP.md", "other.md"),
        encoding="utf-8",
    )

    with pytest.raises(
        ReleaseVerificationError,
        match=r"doctrine_source must be SOULMAP\.md, got other\.md",
    ):
        _verify_integrations(tmp_path, "0.11.0")


def test_verify_integrations_rejects_missing_guide(tmp_path: Path) -> None:
    _write_guides(tmp_path)
    (tmp_path / INTEGRATION_GUIDES[-1]).unlink()

    with pytest.raises(ReleaseVerificationError, match="integration guide is missing"):
        _verify_integrations(tmp_path, "0.11.0")


def test_source_members_match_package_boundary(tmp_path: Path) -> None:
    for path in (
        "LICENSE",
        "SOULMAP.md",
        "SKILL.md",
        "skills/frameworks/example.md",
        "src/soulmap/runtime/source_registry.py",
        ".claude-plugin/marketplace.json",
        ".DS_Store",
    ):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n", encoding="utf-8")

    standard = _source_members(tmp_path, include_plugin=False)
    skill = _source_members(tmp_path, include_plugin=True)

    assert "skills/frameworks/example.md" in standard
    assert "src/soulmap/runtime/source_registry.py" not in standard
    assert ".claude-plugin/marketplace.json" not in standard
    assert ".claude-plugin/marketplace.json" in skill
    assert ".DS_Store" not in standard
    assert ".DS_Store" not in skill


def test_verify_archive_rejects_duplicate_member_names(tmp_path: Path) -> None:
    for name in ("LICENSE", "SOULMAP.md", "SKILL.md", "skills/example.md"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("source content\n", encoding="utf-8")

    archive_path = tmp_path / "dist" / "soulmap-ai.zip"
    archive_path.parent.mkdir()
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name in ("LICENSE", "SOULMAP.md", "SKILL.md", "skills/example.md"):
            archive.write(tmp_path / name, arcname=name)
        with pytest.warns(UserWarning, match="Duplicate name"):
            archive.writestr("SKILL.md", "conflicting duplicate\n")

    with pytest.raises(
        ReleaseVerificationError, match="duplicate archive member names"
    ):
        _verify_archive(tmp_path, archive_path, include_plugin=False)


@pytest.mark.parametrize(
    "member_name",
    ["C:/outside.txt", "C:outside.txt", "skills/..\\outside.txt"],
)
def test_verify_archive_rejects_windows_unsafe_member_paths(
    tmp_path: Path, member_name: str
) -> None:
    archive_path = tmp_path / "dist" / "soulmap-ai.zip"
    archive_path.parent.mkdir(parents=True)
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(member_name, "unsafe")

    with pytest.raises(ReleaseVerificationError, match="unsafe archive member path"):
        _verify_archive(tmp_path, archive_path, include_plugin=False)



@pytest.mark.skipif(os.name == "nt", reason="POSIX permits backslashes in filenames")
def test_source_members_applies_distignore_before_member_path_validation(
    tmp_path: Path,
) -> None:
    for path in ("LICENSE", "SOULMAP.md", "SKILL.md"):
        target = tmp_path / path
        target.write_text("fixture\n", encoding="utf-8")
    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "ignored\\name.md").write_text("ignored\n", encoding="utf-8")
    (tmp_path / ".distignore").write_text(
        "skills/ignored\\name.md\n", encoding="utf-8"
    )

    assert "skills/ignored\\name.md" not in _source_members(
        tmp_path, include_plugin=False
    )
