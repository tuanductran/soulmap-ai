from __future__ import annotations

import json
import shutil
import stat
import zipfile
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from scripts.build_soulmate_skills import build_artifacts
from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge import (
    MAX_ARCHIVE_MEMBERS,
    MAX_ARCHIVE_TOTAL_SIZE,
    MAX_MANIFEST_BYTES,
    MAX_SKILL_BYTES,
    SOULMAP_COMPATIBLE_SKILL_IDS,
    LoadedSoulmateSkill,
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
    assert selected.compatibility == ">=0.1.0,<0.2.0"
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


def test_adapter_rejects_archive_with_too_many_members(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    oversized_path = tmp_path / "too-many-members.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            oversized_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            destination.writestr(info, source.read(info))
        for index in range(MAX_ARCHIVE_MEMBERS):
            destination.writestr(f"extra/{index}.txt", b"x")

    with pytest.raises(SoulmateSkillLoadError, match="too many archive members"):
        SoulmateSkillLoader(oversized_path).load(CONTRACT_ID)


def test_adapter_rejects_archive_with_excessive_total_size(tmp_path: Path) -> None:
    source = tmp_path / "too-large.zip"
    with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("large.bin", b"x" * (MAX_ARCHIVE_TOTAL_SIZE + 1))

    with pytest.raises(SoulmateSkillLoadError, match="uncompressed size is too large"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_manifest_digest_mismatch_in_provenance(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    broken_path = tmp_path / "bad-provenance-digest.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            broken_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            content = source.read(info)
            if info.filename == "PROVENANCE.json":
                provenance = json.loads(content.decode("utf-8"))
                provenance["manifest_sha256"] = "0" * 64
                content = (json.dumps(provenance, indent=2) + "\n").encode("utf-8")
            destination.writestr(info, content)

    with pytest.raises(SoulmateSkillLoadError, match="manifest digest mismatch"):
        SoulmateSkillLoader(broken_path).load(CONTRACT_ID)


def test_adapter_rejects_non_deterministic_provenance(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    broken_path = tmp_path / "non-deterministic.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            broken_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            content = source.read(info)
            if info.filename == "PROVENANCE.json":
                provenance = json.loads(content.decode("utf-8"))
                provenance["build"]["deterministic"] = False
                content = (json.dumps(provenance, indent=2) + "\n").encode("utf-8")
            destination.writestr(info, content)

    with pytest.raises(SoulmateSkillLoadError, match="not deterministic"):
        SoulmateSkillLoader(broken_path).load(CONTRACT_ID)


@pytest.mark.parametrize(
    ("variant", "expected"),
    [
        ("not-object", "manifest must be an object"),
        ("schema", "Unsupported Soulmate manifest schema"),
        ("library", "Invalid Soulmate library identity"),
        ("distribution-family", "Invalid Soulmate artifact family"),
        ("distribution-public", "must remain pre-release"),
        ("artifact-family", "Invalid Soulmate artifact family"),
        ("source-of-truth", "Invalid Soulmate manifest source of truth"),
        ("contract-path", "Invalid Soulmate artifact contract"),
        ("contract-formats", "Invalid Soulmate artifact contract"),
        ("empty-entries", "entries must be non-empty"),
        ("entry-object", "entry must be an object"),
        ("entry-required", "entry is incomplete"),
        ("entry-id", "invalid or duplicate ID"),
        ("entry-source", "invalid or duplicate source"),
        ("entry-version", "invalid version"),
        ("entry-owner", "invalid ownership"),
        ("entry-artifact", "invalid artifact"),
        ("entry-consumers", "invalid consumers"),
    ],
)
def test_adapter_rejects_invalid_manifest_variants(
    tmp_path: Path, variant: str, expected: str
) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = manifest["entries"][0]

    if variant == "not-object":
        manifest_path.write_text("[]", encoding="utf-8")
    elif variant == "schema":
        manifest["schema_version"] = "2.0"
    elif variant == "library":
        manifest["library_id"] = "other-library"
    elif variant == "distribution-family":
        manifest["distribution"]["artifact_family"] = "other-artifact"
    elif variant == "distribution-public":
        manifest["distribution"]["public_registry"] = True
    elif variant == "artifact-family":
        manifest["distribution"] = None
        manifest["artifact_family"] = "other-artifact"
    elif variant == "source-of-truth":
        manifest["source_of_truth"] = "other/path"
    elif variant == "contract-path":
        manifest["artifact_contract"]["path"] = "wrong.md"
    elif variant == "contract-formats":
        manifest["artifact_contract"]["formats"] = ["zip"]
    elif variant == "empty-entries":
        manifest["entries"] = []
    elif variant == "entry-object":
        manifest["entries"][0] = "not-an-entry"
    elif variant == "entry-required":
        entry.pop("artifact")
    elif variant == "entry-id":
        entry["id"] = "not-soulmate"
    elif variant == "entry-source":
        entry["source"] = "../escape.md"
    elif variant == "entry-version":
        entry["version"] = ""
    elif variant == "entry-owner":
        entry["owner"] = "SoulMap"
    elif variant == "entry-artifact":
        entry["artifact"] = "soulmap-ai"
    elif variant == "entry-consumers":
        entry["consumers"] = ["unknown-consumer"]
    else:
        raise AssertionError(f"Unhandled manifest test variant: {variant}")

    if variant != "not-object":
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    with pytest.raises(SoulmateSkillLoadError, match=expected):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("schema_version", "Unsupported Soulmate provenance schema"),
        ("library_id", "library identity mismatch"),
        ("artifact_family", "artifact family mismatch"),
        ("artifact_version", "version mismatch"),
        ("file_list", "file list mismatch"),
        ("selected_entries", "entry list mismatch"),
    ],
)
def test_adapter_rejects_provenance_metadata_mismatches(
    tmp_path: Path, field: str, expected: str
) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    broken_path = tmp_path / f"bad-provenance-{field}.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            broken_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            content = source.read(info)
            if info.filename == "PROVENANCE.json":
                provenance = json.loads(content.decode("utf-8"))
                if field == "schema_version":
                    provenance[field] = "2.0"
                elif field == "library_id" or field == "artifact_family":
                    provenance[field] = "other"
                elif field == "artifact_version":
                    provenance[field] = "9.9.9"
                elif field == "file_list" or field == "selected_entries":
                    provenance[field] = []
                content = (json.dumps(provenance, indent=2) + "\n").encode("utf-8")
            destination.writestr(info, content)

    with pytest.raises(SoulmateSkillLoadError, match=expected):
        SoulmateSkillLoader(broken_path).load(CONTRACT_ID)


def test_adapter_rejects_invalid_utf8_skill_content(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    (source / "foundation" / "contracts.md").write_bytes(b"\xff")

    with pytest.raises(SoulmateSkillLoadError, match="Could not read Soulmate skill"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_rejects_oversized_provenance(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    broken_path = tmp_path / "oversized-provenance.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            broken_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            content = source.read(info)
            if info.filename == "PROVENANCE.json":
                content = b"x" * (MAX_MANIFEST_BYTES + 1)
            destination.writestr(info, content)

    with pytest.raises(SoulmateSkillLoadError, match="provenance is too large"):
        SoulmateSkillLoader(broken_path).load(CONTRACT_ID)


def test_adapter_rejects_non_object_provenance(tmp_path: Path) -> None:
    zip_path, _, _, _, _ = build_artifacts(tmp_path / "artifacts")
    broken_path = tmp_path / "non-object-provenance.zip"
    with (
        zipfile.ZipFile(zip_path) as source,
        zipfile.ZipFile(
            broken_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as destination,
    ):
        for info in source.infolist():
            content = source.read(info)
            if info.filename == "PROVENANCE.json":
                content = b"[]"
            destination.writestr(info, content)

    with pytest.raises(SoulmateSkillLoadError, match="provenance must be an object"):
        SoulmateSkillLoader(broken_path).load(CONTRACT_ID)


def test_adapter_rejects_approved_id_absent_from_manifest(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    shutil.copytree(SKILLS_ROOT, source)
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"].pop(0)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(SoulmateSkillLoadError, match="absent from the manifest"):
        SoulmateSkillLoader(source).load(CONTRACT_ID)


def test_adapter_builds_an_immutable_foundation_bundle() -> None:
    adapter = SoulMapSoulmateAdapter(SoulmateSkillLoader(SKILLS_ROOT))

    bundle = adapter.load_foundation_bundle()

    assert bundle.skill_ids == SOULMAP_COMPATIBLE_SKILL_IDS
    assert bundle.get(CONTRACT_ID).compatibility == ">=0.1.0,<0.2.0"
    with pytest.raises(SoulmateSkillLoadError, match="absent from bundle"):
        bundle.get("soulmate.foundation.lifecycle")


class _IncompleteLoader:
    def load_approved(self) -> tuple[LoadedSoulmateSkill, ...]:
        return ()


def test_adapter_rejects_an_incomplete_foundation_bundle() -> None:
    adapter = SoulMapSoulmateAdapter(cast(SoulmateSkillLoader, _IncompleteLoader()))

    with pytest.raises(SoulmateSkillLoadError, match="does not match the approved set"):
        adapter.load_foundation_bundle()


class _VersionMismatchLoader(SoulmateSkillLoader):
    def __init__(self) -> None:
        super().__init__(SKILLS_ROOT)

    def load_approved(self) -> tuple[LoadedSoulmateSkill, ...]:
        skills = super().load_approved()
        return (replace(skills[0], version="9.9.9"), *skills[1:])


class _CompatibilityMismatchLoader(SoulmateSkillLoader):
    def __init__(self) -> None:
        super().__init__(SKILLS_ROOT)

    def load_approved(self) -> tuple[LoadedSoulmateSkill, ...]:
        skills = super().load_approved()
        return (replace(skills[0], compatibility=">=9.0.0,<10.0.0"), *skills[1:])


def test_adapter_rejects_incompatible_bundle_versions() -> None:
    adapter = SoulMapSoulmateAdapter(_VersionMismatchLoader())

    with pytest.raises(SoulmateSkillLoadError, match="incompatible versions"):
        adapter.load_foundation_bundle()


def test_adapter_rejects_incompatible_bundle_ranges() -> None:
    adapter = SoulMapSoulmateAdapter(_CompatibilityMismatchLoader())

    with pytest.raises(SoulmateSkillLoadError, match="incompatible ranges"):
        adapter.load_foundation_bundle()
