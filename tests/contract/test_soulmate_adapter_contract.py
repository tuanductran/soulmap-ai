from __future__ import annotations

import json
import shutil
import stat
import zipfile
from pathlib import Path

import pytest

from scripts.build_soulmate_skills import build_artifacts
from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge import (
    MAX_MANIFEST_BYTES,
    MAX_SKILL_BYTES,
    SOULMAP_COMPATIBLE_SKILL_IDS,
    SoulMapSoulmateAdapter,
    SoulmateSkillLoader,
    SoulmateSkillLoadError,
)

SKILLS_ROOT = REPO_ROOT / "packages" / "soulmate" / "skills"
CONTRACT_ID = "soulmate.foundation.contracts"


def test_adapter_uses_the_explicit_approved_skill_set() -> None:
    assert SOULMAP_COMPATIBLE_SKILL_IDS == (
        "soulmate.foundation.contracts",
        "soulmate.foundation.resource-boundaries",
        "soulmate.foundation.knowledge-resolution",
        "soulmate.foundation.text-normalization",
        "soulmate.foundation.data-validation",
    )


def test_adapter_loads_an_explicit_skill_from_canonical_directory() -> None:
    loaded = SoulmateSkillLoader(SKILLS_ROOT).load(CONTRACT_ID)

    assert loaded.id == CONTRACT_ID
    assert loaded.version == "0.1.0"
    assert loaded.source == "foundation/contracts.md"
    assert loaded.content.startswith("---\n")


def test_adapter_loads_only_approved_entries_without_directory_discovery(
    tmp_path: Path,
) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "foundation" / "undocumented.md").write_text(
        "---\nname: undocumented\ndescription: ignored\nlicense: MIT\n---\n",
        encoding="utf-8",
    )

    loaded = SoulmateSkillLoader(source).load_approved()

    assert tuple(skill.id for skill in loaded) == SOULMAP_COMPATIBLE_SKILL_IDS
    assert all(skill.source != "foundation/undocumented.md" for skill in loaded)


def test_adapter_rejects_a_skill_without_soulmap_compatibility(
    tmp_path: Path,
) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"][0]["consumers"] = ["soulmate-only"]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with pytest.raises(SoulmateSkillLoadError, match="not approved for SoulMap"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_loads_an_explicit_skill_from_verified_zip(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")

    loaded = SoulmateSkillLoader(zip_path).load(CONTRACT_ID)

    assert loaded.id == CONTRACT_ID
    assert loaded.source == "foundation/contracts.md"
    assert loaded.content.startswith("---\n")


def test_adapter_rejects_extra_zip_members(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    unsafe_path = tmp_path / "unsafe.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            unsafe_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            destination.writestr(info, source.read(info))
        destination.writestr("skills/foundation/undocumented.md", b"extra")

    with pytest.raises(SoulmateSkillLoadError, match="file set does not match"):
        SoulmateSkillLoader(unsafe_path).load(CONTRACT_ID)


def test_adapter_rejects_unapproved_ids_before_loading() -> None:
    with pytest.raises(SoulmateSkillLoadError, match="does not approve"):
        SoulmateSkillLoader(SKILLS_ROOT).load("soulmate.foundation.lifecycle")


def test_adapter_facade_delegates_explicit_selection_and_batch_loading() -> None:
    adapter = SoulMapSoulmateAdapter(SoulmateSkillLoader(SKILLS_ROOT))

    selected = adapter.load_foundation_skill(CONTRACT_ID)
    approved = adapter.load_approved_foundation_skills()

    assert selected.id == CONTRACT_ID
    assert tuple(skill.id for skill in approved) == SOULMAP_COMPATIBLE_SKILL_IDS


def test_adapter_rejects_a_missing_source() -> None:
    with pytest.raises(SoulmateSkillLoadError, match="does not exist"):
        SoulmateSkillLoader(Path("/tmp/does-not-exist-soulmate-skills")).load(
            CONTRACT_ID
        )


def test_adapter_rejects_missing_manifest(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    source.mkdir()

    with pytest.raises(SoulmateSkillLoadError, match="manifest is not a regular file"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_missing_selected_skill(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "foundation" / "contracts.md").unlink()

    with pytest.raises(SoulmateSkillLoadError, match="not a regular file"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_oversized_manifest(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "manifest.json").write_bytes(b" " * (MAX_MANIFEST_BYTES + 1))

    with pytest.raises(SoulmateSkillLoadError, match="manifest is too large"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_oversized_selected_skill(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "foundation" / "contracts.md").write_bytes(b"-" * (MAX_SKILL_BYTES + 1))

    with pytest.raises(SoulmateSkillLoadError, match="skill is too large"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_malformed_manifest(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "manifest.json").write_text("not-json", encoding="utf-8")

    with pytest.raises(SoulmateSkillLoadError, match="manifest is invalid"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_malformed_skill_content(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "foundation" / "contracts.md").write_text(
        "# no front matter\n", encoding="utf-8"
    )

    with pytest.raises(SoulmateSkillLoadError, match="malformed front matter"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_nul_in_skill_content(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "foundation" / "contracts.md").write_text(
        "---\nname: contracts\ndescription: x\nlicense: MIT\n---\n\x00",
        encoding="utf-8",
    )

    with pytest.raises(SoulmateSkillLoadError, match="contains a NUL"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_non_zip_source(tmp_path: Path) -> None:
    source = tmp_path / "not-an-artifact.zip"
    source.write_text("not a zip", encoding="utf-8")

    with pytest.raises(
        SoulmateSkillLoadError, match="Could not read Soulmate artifact"
    ):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_zip_without_manifest(tmp_path: Path) -> None:
    source = tmp_path / "missing-manifest.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("README.md", "readme")

    with pytest.raises(SoulmateSkillLoadError, match=r"missing manifest\.json"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_unsafe_zip_member(tmp_path: Path) -> None:
    source = tmp_path / "unsafe-member.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("../escape.md", "bad")

    with pytest.raises(SoulmateSkillLoadError, match="Unsafe Soulmate artifact member"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_directory_symlink_escape(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "contracts.md").write_text(
        "---\nname: outside\ndescription: outside\nlicense: MIT\n---\n",
        encoding="utf-8",
    )
    (source / "foundation").rename(source / "foundation-real")
    (source / "foundation").symlink_to(outside, target_is_directory=True)

    with pytest.raises(SoulmateSkillLoadError, match="escapes the source root"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_symlinked_selected_file(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    target = source / "foundation" / "resource-boundaries.md"
    target.unlink()
    target.symlink_to(source / "foundation" / "contracts.md")

    with pytest.raises(SoulmateSkillLoadError, match="not a regular file"):
        SoulmateSkillLoader(source).load("soulmate.foundation.resource-boundaries")


def test_adapter_rejects_duplicate_zip_members(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    duplicate_path = tmp_path / "duplicate.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            duplicate_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            destination.writestr(info, source.read(info))
        destination.writestr("README.md", b"duplicate")

    with pytest.raises(SoulmateSkillLoadError, match="duplicate members"):
        SoulmateSkillLoader(duplicate_path).load(CONTRACT_ID)


def test_adapter_rejects_symlink_like_zip_member(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    symlink_path = tmp_path / "symlink.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            symlink_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            destination.writestr(info, source.read(info))
        info = zipfile.ZipInfo("skills/foundation/link.md")
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        destination.writestr(info, b"link")

    with pytest.raises(SoulmateSkillLoadError, match="Symlink-like"):
        SoulmateSkillLoader(symlink_path).load(CONTRACT_ID)


def test_adapter_rejects_oversized_zip_manifest(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    oversized_path = tmp_path / "oversized-manifest.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            oversized_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            content = source.read(info)
            if info.filename == "manifest.json":
                content = b" " * (MAX_MANIFEST_BYTES + 1)
            destination.writestr(info, content)

    with pytest.raises(SoulmateSkillLoadError, match="manifest is too large"):
        SoulmateSkillLoader(oversized_path).load(CONTRACT_ID)
