"""Verify isolated Soulmate AI skill artifacts fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "1.0"

MAX_MEMBERS = 128
MAX_MEMBER_SIZE = 512 * 1024
MAX_TOTAL_SIZE = 4 * 1024 * 1024
FORBIDDEN_PATH_PARTS = {
    ".claude",
    ".git",
    ".github",
    "dist",
    "reference",
    "src",
    "tests",
    "soulmap",
}
FORBIDDEN_SUFFIXES = {".lock", ".py", ".pyc", ".toml"}
FORBIDDEN_CONTENT_MARKERS = (
    b"-----BEGIN PRIVATE KEY-----",
    b"-----BEGIN RSA PRIVATE KEY-----",
)
DRIVE_PATH = re.compile(r"^[A-Za-z]:")
REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "artifact-contract.md",
    "manifest.json",
    "PROVENANCE.json",
}


class SoulmateSkillsVerificationError(ValueError):
    """Raised when an AI-facing Soulmate artifact violates its contract."""


def _json(path_name: str, content: bytes) -> dict[str, Any]:
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SoulmateSkillsVerificationError(
            f"{path_name} is not valid UTF-8 JSON"
        ) from error
    if not isinstance(value, dict):
        raise SoulmateSkillsVerificationError(f"{path_name} must contain a JSON object")
    return value


def _check_member_path(name: str) -> str:
    """Validate and normalize an archive member path."""

    if not name or "\\" in name or name.startswith("/") or DRIVE_PATH.match(name):
        raise SoulmateSkillsVerificationError(f"unsafe archive member path: {name}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise SoulmateSkillsVerificationError(f"unsafe archive member path: {name}")
    normalized = path.as_posix()
    if normalized != name:
        raise SoulmateSkillsVerificationError(f"unsafe archive member path: {name}")
    parts = {part.casefold() for part in path.parts}
    if parts.intersection(FORBIDDEN_PATH_PARTS):
        raise SoulmateSkillsVerificationError(f"forbidden artifact path: {name}")
    if any(name.casefold().endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
        raise SoulmateSkillsVerificationError(f"forbidden artifact file type: {name}")
    return normalized


def _expected_files(manifest: dict[str, Any]) -> set[str]:
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SoulmateSkillsVerificationError(
            "manifest entries must be a non-empty list"
        )
    expected = set(REQUIRED_FILES)
    for entry in entries:
        if not isinstance(entry, dict):
            raise SoulmateSkillsVerificationError("manifest entry must be an object")
        source = entry.get("source")
        if (
            not isinstance(source, str)
            or not (source.startswith("foundation/") or source.startswith("companion/"))
            or not source.endswith(".md")
        ):
            raise SoulmateSkillsVerificationError(
                "manifest contains an invalid skill source"
            )
        expected.add(f"skills/{source}")
    return expected


def _validate_manifest(
    manifest: dict[str, Any], expected_version: str | None
) -> set[str]:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise SoulmateSkillsVerificationError("unsupported manifest schema")
    if manifest.get("library_id") != "soulmate-ai":
        raise SoulmateSkillsVerificationError("manifest library_id is not soulmate-ai")
    if manifest.get("artifact_family") != "soulmate-ai":
        raise SoulmateSkillsVerificationError(
            "manifest artifact_family is not soulmate-ai"
        )
    if manifest.get("source_of_truth") != "packages/soulmate/skills":
        raise SoulmateSkillsVerificationError("manifest source_of_truth is invalid")
    artifact_contract = manifest.get("artifact_contract")
    if not isinstance(artifact_contract, dict):
        raise SoulmateSkillsVerificationError(
            "manifest artifact_contract is incomplete"
        )
    if artifact_contract.get("path") != "artifact-contract.md":
        raise SoulmateSkillsVerificationError(
            "manifest artifact contract path is invalid"
        )
    if artifact_contract.get("formats") != ["zip", "skill"]:
        raise SoulmateSkillsVerificationError(
            "manifest artifact contract formats are invalid"
        )
    if artifact_contract.get("content_root") != "skills":
        raise SoulmateSkillsVerificationError(
            "manifest artifact contract content_root is invalid"
        )
    required_files = artifact_contract.get("required_files")
    if (
        not isinstance(required_files, list)
        or len(required_files) != len(REQUIRED_FILES)
        or set(required_files) != REQUIRED_FILES
    ):
        raise SoulmateSkillsVerificationError(
            "manifest artifact contract required_files are invalid"
        )
    version = manifest.get("artifact_version")
    if not isinstance(version, str) or not version:
        raise SoulmateSkillsVerificationError("manifest artifact_version is invalid")
    if expected_version is not None and version != expected_version:
        raise SoulmateSkillsVerificationError(
            f"expected artifact version {expected_version}, found {version}"
        )
    compatibility = manifest.get("compatibility")
    if not isinstance(compatibility, dict) or not compatibility.get("soulmate_package"):
        raise SoulmateSkillsVerificationError("manifest compatibility is incomplete")
    entries = manifest["entries"]
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    sources = [entry.get("source") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(set(ids)) or len(sources) != len(set(sources)):
        raise SoulmateSkillsVerificationError(
            "manifest contains duplicate ids or sources"
        )
    for entry in entries:
        consumers = entry.get("consumers") if isinstance(entry, dict) else None
        if (
            not isinstance(entry, dict)
            or entry.get("owner") != "Soulmate"
            or entry.get("kind") not in {"foundation", "companion"}
            or not isinstance(consumers, list)
            or not consumers
            or any(
                not isinstance(consumer, str)
                or consumer not in {"soulmate-only", "soulmap-compatible"}
                for consumer in consumers
            )
            or len(consumers) != len(set(consumers))
            or entry.get("artifact") != "soulmate-ai"
            or entry.get("version") != version
        ):
            raise SoulmateSkillsVerificationError(
                "manifest contains invalid entry metadata"
            )
    return _expected_files(manifest)


def _validate_provenance(
    provenance: dict[str, Any],
    manifest: dict[str, Any],
    manifest_bytes: bytes,
    expected_files: set[str],
) -> None:
    if provenance.get("schema_version") != SCHEMA_VERSION:
        raise SoulmateSkillsVerificationError("unsupported provenance schema")
    if provenance.get("library_id") != manifest.get("library_id"):
        raise SoulmateSkillsVerificationError(
            "provenance library_id does not match manifest"
        )
    if provenance.get("artifact_family") != manifest.get("artifact_family"):
        raise SoulmateSkillsVerificationError(
            "provenance artifact_family does not match manifest"
        )
    if provenance.get("artifact_version") != manifest.get("artifact_version"):
        raise SoulmateSkillsVerificationError(
            "provenance artifact_version does not match manifest"
        )
    if provenance.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
        raise SoulmateSkillsVerificationError(
            "provenance manifest digest does not match manifest"
        )
    file_list = provenance.get("file_list")
    if file_list != sorted(expected_files):
        raise SoulmateSkillsVerificationError(
            "provenance file list does not match artifact"
        )
    selected_entries = provenance.get("selected_entries")
    manifest_ids = [entry["id"] for entry in manifest["entries"]]
    if selected_entries != manifest_ids:
        raise SoulmateSkillsVerificationError(
            "provenance selected entries do not match manifest"
        )
    build = provenance.get("build")
    if not isinstance(build, dict) or build.get("deterministic") is not True:
        raise SoulmateSkillsVerificationError(
            "provenance does not claim a deterministic build"
        )


def verify_archive(
    path: Path, *, expected_version: str | None = None
) -> dict[str, Any]:
    """Verify one Soulmate AI archive and return its parsed manifest."""

    if not path.is_file() or not zipfile.is_zipfile(path):
        raise SoulmateSkillsVerificationError(f"not a valid ZIP artifact: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_MEMBERS:
                raise SoulmateSkillsVerificationError(
                    "artifact has too many archive members"
                )
            names = [_check_member_path(info.filename) for info in infos]
            if len(names) != len(set(names)):
                raise SoulmateSkillsVerificationError("duplicate archive members")
            total_size = 0
            contents: dict[str, bytes] = {}
            for info, name in zip(infos, names, strict=True):
                mode = stat.S_IFMT(info.external_attr >> 16)
                if mode == stat.S_IFLNK:
                    raise SoulmateSkillsVerificationError(
                        f"symlink-like archive member: {name}"
                    )
                if info.file_size > MAX_MEMBER_SIZE:
                    raise SoulmateSkillsVerificationError(
                        f"archive member is too large: {name}"
                    )
                total_size += info.file_size
                if total_size > MAX_TOTAL_SIZE:
                    raise SoulmateSkillsVerificationError(
                        "artifact uncompressed size is too large"
                    )
                contents[name] = archive.read(info)
    except zipfile.BadZipFile as error:
        raise SoulmateSkillsVerificationError(
            f"invalid ZIP artifact: {path}"
        ) from error

    manifest = _json("manifest.json", contents.get("manifest.json", b""))
    expected_files = _validate_manifest(manifest, expected_version)
    if set(contents) != expected_files:
        unexpected = sorted(set(contents).difference(expected_files))
        missing = sorted(expected_files.difference(contents))
        raise SoulmateSkillsVerificationError(
            f"artifact file set mismatch; missing={missing}, unexpected={unexpected}"
        )
    for name, content in contents.items():
        if name == "artifact-contract.md" or name.startswith("skills/"):
            if b"\x00" in content:
                raise SoulmateSkillsVerificationError(
                    f"skill contains a NUL byte: {name}"
                )
            try:
                _validate_skill_markdown_content(name, content)
            except SoulmateSkillsVerificationError:
                raise
            except ValueError as error:
                raise SoulmateSkillsVerificationError(str(error)) from error
    provenance = _json("PROVENANCE.json", contents["PROVENANCE.json"])
    _validate_provenance(
        provenance, manifest, contents["manifest.json"], expected_files
    )
    return manifest


def _validate_skill_markdown_content(name: str, content: bytes) -> None:
    del name
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SoulmateSkillsVerificationError("skill is not valid UTF-8") from error
    if any(marker in content for marker in FORBIDDEN_CONTENT_MARKERS):
        raise SoulmateSkillsVerificationError(
            "skill contains a high-confidence secret marker"
        )
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise SoulmateSkillsVerificationError("skill has malformed front matter")
    front_matter = text[4:].split("\n---\n", 1)[0]
    required = ("name:", "description:", "license:")
    if not all(
        any(line.startswith(prefix) for line in front_matter.splitlines())
        for prefix in required
    ):
        raise SoulmateSkillsVerificationError("skill has incomplete front matter")


def _verify_checksums(checksum_path: Path, artifacts: list[Path]) -> None:
    if not checksum_path.is_file():
        raise SoulmateSkillsVerificationError(f"missing checksum file: {checksum_path}")
    records: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        if separator and re.fullmatch(r"[0-9a-f]{64}", digest) and name:
            records[name] = digest
        else:
            raise SoulmateSkillsVerificationError("malformed SHA256SUMS record")
    expected_names = {artifact.name for artifact in artifacts}
    if set(records) != expected_names:
        raise SoulmateSkillsVerificationError("SHA256SUMS does not match artifact set")
    for artifact in artifacts:
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if records[artifact.name] != actual:
            raise SoulmateSkillsVerificationError(f"checksum mismatch: {artifact.name}")


def verify_artifacts(
    zip_path: Path,
    skill_path: Path,
    *,
    expected_version: str | None = None,
    checksum_path: Path | None = None,
) -> dict[str, Any]:
    """Verify the ZIP and SKILL projections as one artifact set."""

    if zip_path.name != "soulmate-ai.zip":
        raise SoulmateSkillsVerificationError("unexpected ZIP artifact name")
    if skill_path.name != "soulmate-ai.skill":
        raise SoulmateSkillsVerificationError("unexpected SKILL artifact name")
    zip_manifest = verify_archive(zip_path, expected_version=expected_version)
    skill_manifest = verify_archive(skill_path, expected_version=expected_version)
    if zip_path.read_bytes() != skill_path.read_bytes():
        raise SoulmateSkillsVerificationError(
            ".zip and .skill artifacts are not byte-identical"
        )
    if zip_manifest != skill_manifest:
        raise SoulmateSkillsVerificationError(".zip and .skill manifests do not match")
    if checksum_path is not None:
        _verify_checksums(checksum_path, [zip_path, skill_path])
    return zip_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--skill", type=Path, required=True)
    parser.add_argument("--version")
    parser.add_argument("--checksums", type=Path)
    args = parser.parse_args(argv)
    manifest = verify_artifacts(
        args.zip.resolve(),
        args.skill.resolve(),
        expected_version=args.version,
        checksum_path=args.checksums.resolve() if args.checksums else None,
    )
    print(
        f"PASS: verified Soulmate skills {manifest['artifact_version']} "
        f"({len(manifest['entries'])} entries)"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SoulmateSkillsVerificationError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1) from error
