from __future__ import annotations

import json
import stat
import warnings
import zipfile
from pathlib import Path

import pytest

from scripts.build_soulmate_skills import (
    MANIFEST_PATH,
    PACKAGE_ROOT,
    SKILLS_ROOT,
    SoulmateSkillsBuildError,
    build_artifacts,
    load_manifest,
    validate_manifest,
)
from scripts.verify_soulmate_skills import (
    SoulmateSkillsVerificationError,
    verify_archive,
    verify_artifacts,
)


def _build(tmp_path: Path) -> tuple[Path, Path, Path]:
    output = tmp_path / "out"
    zip_path, skill_path, _, _, checksums = build_artifacts(
        output, source_commit="test-commit"
    )
    return zip_path, skill_path, checksums


def _read_members(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {info.filename: archive.read(info) for info in archive.infolist()}


def _write_archive(
    path: Path,
    members: dict[str, bytes],
    *,
    modes: dict[str, int] | None = None,
    comment: bytes = b"",
) -> Path:
    modes = modes or {}
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.comment = comment
        for name, content in members.items():
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            if name in modes:
                info.external_attr = modes[name] << 16
            archive.writestr(info, content)
    return path


def test_builder_creates_verified_zip_and_skill_projections(tmp_path: Path) -> None:
    zip_path, skill_path, checksums = _build(tmp_path)

    manifest = verify_artifacts(
        zip_path,
        skill_path,
        expected_version="0.1.0",
        checksum_path=checksums,
    )

    assert len(manifest["entries"]) == 11
    assert zip_path.read_bytes() == skill_path.read_bytes()
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "artifact-contract.md" in names
    assert "skills/foundation/contracts.md" in names
    assert not any(name.startswith("src/") for name in names)
    assert not any("soulmap" in name.casefold() for name in names)


def test_builder_is_byte_deterministic_for_same_source(tmp_path: Path) -> None:
    first = _build(tmp_path / "first")
    second = _build(tmp_path / "second")

    assert first[0].read_bytes() == second[0].read_bytes()
    assert first[1].read_bytes() == second[1].read_bytes()


def test_projection_contains_artifact_contract_and_normalized_entries() -> None:
    manifest, entries = load_manifest()

    assert manifest["artifact_contract"] == {
        "path": "artifact-contract.md",
        "formats": ["zip", "skill"],
        "content_root": "skills",
        "required_files": [
            "README.md",
            "LICENSE",
            "artifact-contract.md",
            "manifest.json",
            "PROVENANCE.json",
        ],
    }
    assert all(entry["source"].startswith("foundation/") for entry in entries)


def test_manifest_validation_rejects_missing_artifact_contract() -> None:
    manifest, _ = load_manifest()
    manifest.pop("artifact_contract")

    with pytest.raises(SoulmateSkillsBuildError, match="missing fields"):
        validate_manifest(manifest, source_root=None)


@pytest.mark.parametrize(
    ("field", "value", "match"),
    [
        ("source_of_truth", "skills", "source_of_truth"),
        ("library_id", "soulmap-ai", "library_id"),
        ("distribution", {"artifact_family": "soulmap"}, "artifact_family"),
        (
            "artifact_contract",
            {
                "path": "../contract.md",
                "formats": ["zip", "skill"],
                "content_root": "skills",
            },
            "artifact contract path",
        ),
    ],
)
def test_manifest_validation_rejects_boundary_mutations(
    field: str, value: object, match: str
) -> None:
    manifest, _ = load_manifest()
    manifest[field] = value

    with pytest.raises(SoulmateSkillsBuildError, match=match):
        validate_manifest(manifest, source_root=None)


def test_verifier_rejects_unexpected_artifact_names(tmp_path: Path) -> None:
    zip_path, skill_path, _ = _build(tmp_path / "valid")

    with pytest.raises(
        SoulmateSkillsVerificationError, match="unexpected ZIP artifact name"
    ):
        verify_artifacts(zip_path.with_name("wrong.zip"), skill_path)

    with pytest.raises(
        SoulmateSkillsVerificationError, match="unexpected SKILL artifact name"
    ):
        verify_artifacts(zip_path, skill_path.with_name("wrong.skill"))


def test_verifier_rejects_forbidden_soulmap_path(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["src/soulmap/secret.py"] = b"bad"
    unsafe = _write_archive(tmp_path / "unsafe.zip", members)

    with pytest.raises(
        SoulmateSkillsVerificationError, match="forbidden artifact path"
    ):
        verify_archive(unsafe)


def test_verifier_rejects_parent_traversal(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["../escape.md"] = b"bad"
    unsafe = _write_archive(tmp_path / "unsafe.zip", members)

    with pytest.raises(
        SoulmateSkillsVerificationError, match="unsafe archive member path"
    ):
        verify_archive(unsafe)


def test_verifier_rejects_duplicate_archive_members(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    duplicate = tmp_path / "duplicate.zip"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(duplicate, "w") as archive:
            for name, content in members.items():
                archive.writestr(name, content)
            archive.writestr("README.md", b"different")

    with pytest.raises(
        SoulmateSkillsVerificationError, match="duplicate archive members"
    ):
        verify_archive(duplicate)


def test_verifier_rejects_symlink_like_member(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["skills/foundation/link.md"] = b"link"
    unsafe = _write_archive(
        tmp_path / "symlink.zip",
        members,
        modes={"skills/foundation/link.md": stat.S_IFLNK | 0o777},
    )

    with pytest.raises(SoulmateSkillsVerificationError, match="symlink-like"):
        verify_archive(unsafe)


def test_verifier_rejects_secret_marker(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["skills/foundation/contracts.md"] = (
        b"---\nname: x\ndescription: x\nlicense: MIT\n---\n-----BEGIN PRIVATE KEY-----"
    )
    unsafe = _write_archive(tmp_path / "secret.zip", members)

    with pytest.raises(SoulmateSkillsVerificationError, match="secret marker"):
        verify_archive(unsafe)


def test_verifier_rejects_unexpected_python_file(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["skills/foundation/secret.py"] = b"print('bad')"
    unsafe = _write_archive(tmp_path / "python.zip", members)

    with pytest.raises(
        SoulmateSkillsVerificationError, match="forbidden artifact file type"
    ):
        verify_archive(unsafe)


def test_verifier_rejects_missing_manifest_entry_file(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members.pop("skills/foundation/contracts.md")
    unsafe = _write_archive(tmp_path / "missing.zip", members)

    with pytest.raises(SoulmateSkillsVerificationError, match="file set mismatch"):
        verify_archive(unsafe)


def test_verifier_rejects_malformed_skill_front_matter(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["skills/foundation/contracts.md"] = b"# Missing front matter\n"
    unsafe = _write_archive(tmp_path / "malformed.zip", members)

    with pytest.raises(SoulmateSkillsVerificationError, match="malformed front matter"):
        verify_archive(unsafe)


def test_verifier_rejects_invalid_required_file_contract(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    manifest = json.loads(members["manifest.json"])
    manifest["artifact_contract"]["required_files"] = ["README.md"]
    members["manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode()
    unsafe = _write_archive(tmp_path / "required-files.zip", members)

    with pytest.raises(
        SoulmateSkillsVerificationError, match="required_files are invalid"
    ):
        verify_archive(unsafe)


def test_verifier_rejects_manifest_version_mismatch(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    manifest = json.loads(members["manifest.json"])
    manifest["artifact_version"] = "9.9.9"
    members["manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode()
    unsafe = _write_archive(tmp_path / "version.zip", members)

    with pytest.raises(SoulmateSkillsVerificationError, match="invalid entry metadata"):
        verify_archive(unsafe)


def test_verifier_rejects_oversized_member(tmp_path: Path) -> None:
    zip_path, _, _ = _build(tmp_path / "valid")
    members = _read_members(zip_path)
    members["oversized.md"] = b"x" * (512 * 1024 + 1)
    unsafe = _write_archive(tmp_path / "large.zip", members)

    with pytest.raises(SoulmateSkillsVerificationError, match="too large"):
        verify_archive(unsafe)


def test_verifier_rejects_non_identical_zip_and_skill(tmp_path: Path) -> None:
    zip_path, skill_path, _ = _build(tmp_path / "valid")
    _write_archive(skill_path, _read_members(zip_path), comment=b"different")

    with pytest.raises(SoulmateSkillsVerificationError, match="not byte-identical"):
        verify_artifacts(zip_path, skill_path)


def test_verifier_rejects_checksum_mismatch(tmp_path: Path) -> None:
    zip_path, skill_path, checksums = _build(tmp_path / "valid")
    checksum_text = checksums.read_text(encoding="utf-8")
    checksums.write_text("0" + checksum_text[1:], encoding="utf-8")

    with pytest.raises(SoulmateSkillsVerificationError, match="checksum mismatch"):
        verify_artifacts(zip_path, skill_path, checksum_path=checksums)


def test_builder_source_constants_remain_isolated() -> None:
    assert PACKAGE_ROOT.name == "soulmate"
    assert SKILLS_ROOT == PACKAGE_ROOT / "skills"
    assert MANIFEST_PATH == SKILLS_ROOT / "manifest.json"
