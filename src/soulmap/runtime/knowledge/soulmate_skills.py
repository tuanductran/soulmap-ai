"""Explicit loading of approved Soulmate foundation skills by SoulMap.

This module is a SoulMap consumer seam. It never discovers or activates every file
under the Soulmate skill directory. A caller must provide the canonical Soulmate
skills directory or an already-built Soulmate ZIP/SKILL artifact, and the adapter
only permits the stable IDs explicitly approved by SoulMap's generated consumer projection.
"""

from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ._soulmate_consumer_scope import APPROVED_SOULMATE_SKILLS

SOULMATE_MANIFEST_NAME = "manifest.json"
SOULMATE_ARTIFACT_ROOT = "skills"
MAX_MANIFEST_BYTES = 64 * 1024
MAX_SKILL_BYTES = 512 * 1024
MAX_ARCHIVE_MEMBERS = 128
MAX_ARCHIVE_TOTAL_SIZE = 4 * 1024 * 1024

# These are the neutral capabilities approved by SoulMap's generated consumer
# projection. Every ID must also explicitly declare ``soulmap-compatible`` in
# the canonical Soulmate manifest. P1/P2 entries remain Soulmate-only.
SOULMAP_COMPATIBLE_SKILL_IDS: tuple[str, ...] = tuple(
    entry[0] for entry in APPROVED_SOULMATE_SKILLS
)


class SoulmateSkillLoadError(ValueError):
    """Raised when an explicit Soulmate skill load violates its contract."""


@dataclass(frozen=True)
class LoadedSoulmateSkill:
    """A validated, read-only Soulmate skill selected by stable ID."""

    id: str
    version: str
    compatibility: str
    source: str
    content: str


@dataclass(frozen=True)
class SoulmateFoundationBundle:
    """An immutable, explicitly approved set of Soulmate foundation skills."""

    skills: tuple[LoadedSoulmateSkill, ...]

    @property
    def skill_ids(self) -> tuple[str, ...]:
        return tuple(skill.id for skill in self.skills)

    @property
    def version(self) -> str:
        return self.skills[0].version

    @property
    def compatibility(self) -> str:
        return self.skills[0].compatibility

    def get(self, skill_id: str) -> LoadedSoulmateSkill:
        for skill in self.skills:
            if skill.id == skill_id:
                return skill
        raise SoulmateSkillLoadError(
            f"Soulmate foundation skill is absent from bundle: {skill_id}"
        )


class SoulmateSkillLoader:
    """Load one manifest-selected skill from a directory or ZIP/SKILL artifact."""

    def __init__(self, source: Path) -> None:
        self.source = source

    def load(self, skill_id: str) -> LoadedSoulmateSkill:
        """Load one approved skill ID without scanning for additional skills."""

        if skill_id not in SOULMAP_COMPATIBLE_SKILL_IDS:
            raise SoulmateSkillLoadError(
                f"SoulMap adapter does not approve Soulmate skill: {skill_id}"
            )

        if self.source.is_dir():
            manifest = _read_manifest_file(self.source / SOULMATE_MANIFEST_NAME)
            content_reader = _DirectoryContentReader(self.source)
            return _load_selected_skill(manifest, content_reader, skill_id)

        if self.source.is_file():
            return _load_from_archive(self.source, skill_id)

        raise SoulmateSkillLoadError(
            f"Soulmate skill source does not exist: {self.source}"
        )

    def load_approved(self) -> tuple[LoadedSoulmateSkill, ...]:
        """Load the fixed approved set in declaration order."""

        return tuple(self.load(skill_id) for skill_id in SOULMAP_COMPATIBLE_SKILL_IDS)


class SoulMapSoulmateAdapter:
    """Thin SoulMap-owned seam for explicit Soulmate skill consumption."""

    def __init__(self, loader: SoulmateSkillLoader) -> None:
        self._loader = loader

    def load_foundation_skill(self, skill_id: str) -> LoadedSoulmateSkill:
        """Map an explicitly requested approved ID to the foundation loader."""

        return self._loader.load(skill_id)

    def load_approved_foundation_skills(self) -> tuple[LoadedSoulmateSkill, ...]:
        """Return only the five foundation skills approved for SoulMap."""

        return self._loader.load_approved()

    def load_foundation_bundle(self) -> SoulmateFoundationBundle:
        """Compose the fixed approved foundation set without adding policy."""

        skills = self._loader.load_approved()
        if tuple(skill.id for skill in skills) != SOULMAP_COMPATIBLE_SKILL_IDS:
            raise SoulmateSkillLoadError(
                "Soulmate foundation bundle does not match the approved set"
            )
        if len({skill.version for skill in skills}) != 1:
            raise SoulmateSkillLoadError(
                "Soulmate foundation bundle has incompatible versions"
            )
        if len({skill.compatibility for skill in skills}) != 1:
            raise SoulmateSkillLoadError(
                "Soulmate foundation bundle has incompatible ranges"
            )
        return SoulmateFoundationBundle(skills=skills)


class _DirectoryContentReader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def read(self, source: str) -> str:
        root = self.root.resolve()
        raw_path = root / source
        if raw_path.is_symlink():
            raise SoulmateSkillLoadError(
                f"Soulmate skill source is not a regular file: {source}"
            )
        path = raw_path.resolve()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise SoulmateSkillLoadError(
                f"Soulmate skill source escapes the source root: {source}"
            ) from error
        try:
            if not path.is_file() or path.is_symlink():
                raise SoulmateSkillLoadError(
                    f"Soulmate skill source is not a regular file: {source}"
                )
            if path.stat().st_size > MAX_SKILL_BYTES:
                raise SoulmateSkillLoadError(f"Soulmate skill is too large: {source}")
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise SoulmateSkillLoadError(
                f"Could not read Soulmate skill source: {source}"
            ) from error


def _read_manifest_file(path: Path) -> dict[str, Any]:
    try:
        if not path.is_file() or path.is_symlink():
            raise SoulmateSkillLoadError("Soulmate manifest is not a regular file")
        if path.stat().st_size > MAX_MANIFEST_BYTES:
            raise SoulmateSkillLoadError("Soulmate manifest is too large")
        value = json.loads(path.read_text(encoding="utf-8"))
    except SoulmateSkillLoadError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SoulmateSkillLoadError("Soulmate manifest is invalid") from error
    return _validate_manifest(value)


def _load_from_archive(path: Path, skill_id: str) -> LoadedSoulmateSkill:
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_MEMBERS:
                raise SoulmateSkillLoadError(
                    "Soulmate artifact has too many archive members"
                )
            total_size = sum(info.file_size for info in infos)
            if total_size > MAX_ARCHIVE_TOTAL_SIZE:
                raise SoulmateSkillLoadError(
                    "Soulmate artifact uncompressed size is too large"
                )
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise SoulmateSkillLoadError(
                    "Soulmate artifact contains duplicate members"
                )
            info_by_name = {}
            for info in infos:
                _validate_archive_member(info)
                info_by_name[info.filename] = info
            manifest_info = info_by_name.get(SOULMATE_MANIFEST_NAME)
            if manifest_info is None:
                raise SoulmateSkillLoadError(
                    "Soulmate artifact is missing manifest.json"
                )
            if manifest_info.file_size > MAX_MANIFEST_BYTES:
                raise SoulmateSkillLoadError("Soulmate manifest is too large")
            manifest_bytes = archive.read(manifest_info)
            manifest = _validate_manifest(json.loads(manifest_bytes.decode("utf-8")))
            expected_names = {
                "README.md",
                "LICENSE",
                "artifact-contract.md",
                "manifest.json",
                "PROVENANCE.json",
                *{
                    f"{SOULMATE_ARTIFACT_ROOT}/{entry['source']}"
                    for entry in manifest["entries"]
                },
            }
            if set(info_by_name) != expected_names:
                raise SoulmateSkillLoadError(
                    "Soulmate artifact file set does not match its manifest"
                )
            provenance_info = info_by_name["PROVENANCE.json"]
            if provenance_info.file_size > MAX_MANIFEST_BYTES:
                raise SoulmateSkillLoadError("Soulmate provenance is too large")
            _validate_provenance(
                json.loads(archive.read(provenance_info).decode("utf-8")),
                manifest,
                manifest_bytes,
                expected_names,
            )
            entry = _select_entry(manifest, skill_id)
            member = f"{SOULMATE_ARTIFACT_ROOT}/{entry['source']}"
            skill_info = info_by_name[member]
            content = archive.read(skill_info).decode("utf-8")
            return _validate_skill_content(entry, content)
    except SoulmateSkillLoadError:
        raise
    except (
        OSError,
        zipfile.BadZipFile,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise SoulmateSkillLoadError(
            f"Could not read Soulmate artifact: {path}"
        ) from error


def _validate_archive_member(info: zipfile.ZipInfo) -> None:
    name = info.filename
    path = PurePosixPath(name)
    if not name or "\\" in name or path.is_absolute() or ".." in path.parts:
        raise SoulmateSkillLoadError(f"Unsafe Soulmate artifact member: {name}")
    mode = (info.external_attr >> 16) & 0o170000
    if mode == stat.S_IFLNK:
        raise SoulmateSkillLoadError(f"Symlink-like Soulmate artifact member: {name}")


def _validate_provenance(
    provenance: Any,
    manifest: dict[str, Any],
    manifest_bytes: bytes,
    expected_names: set[str],
) -> None:
    if not isinstance(provenance, dict):
        raise SoulmateSkillLoadError("Soulmate provenance must be an object")
    if provenance.get("schema_version") != "1.0":
        raise SoulmateSkillLoadError("Unsupported Soulmate provenance schema")
    if provenance.get("library_id") != manifest.get("library_id"):
        raise SoulmateSkillLoadError("Soulmate provenance library identity mismatch")
    if provenance.get("artifact_family") != manifest.get("artifact_family"):
        raise SoulmateSkillLoadError("Soulmate provenance artifact family mismatch")
    if provenance.get("artifact_version") != manifest.get("artifact_version"):
        raise SoulmateSkillLoadError("Soulmate provenance version mismatch")
    if provenance.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
        raise SoulmateSkillLoadError("Soulmate provenance manifest digest mismatch")
    if provenance.get("file_list") != sorted(expected_names):
        raise SoulmateSkillLoadError("Soulmate provenance file list mismatch")
    manifest_ids = [entry["id"] for entry in manifest["entries"]]
    if provenance.get("selected_entries") != manifest_ids:
        raise SoulmateSkillLoadError("Soulmate provenance entry list mismatch")
    build = provenance.get("build")
    if not isinstance(build, dict) or build.get("deterministic") is not True:
        raise SoulmateSkillLoadError("Soulmate provenance is not deterministic")


def _validate_manifest(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SoulmateSkillLoadError("Soulmate manifest must be an object")
    if value.get("schema_version") != "1.0":
        raise SoulmateSkillLoadError("Unsupported Soulmate manifest schema")
    if value.get("library_id") != "soulmate-ai":
        raise SoulmateSkillLoadError("Invalid Soulmate library identity")
    artifact_family = value.get("artifact_family")
    distribution = value.get("distribution")
    if distribution is not None:
        if (
            not isinstance(distribution, dict)
            or distribution.get("artifact_family") != "soulmate-ai"
        ):
            raise SoulmateSkillLoadError("Invalid Soulmate artifact family")
        if distribution.get("public_registry") is not False:
            raise SoulmateSkillLoadError("Soulmate artifact must remain pre-release")
    elif artifact_family != "soulmate-ai":
        raise SoulmateSkillLoadError("Invalid Soulmate artifact family")
    if value.get("source_of_truth") != "packages/soulmate/skills":
        raise SoulmateSkillLoadError("Invalid Soulmate manifest source of truth")
    artifact_contract = value.get("artifact_contract")
    if (
        not isinstance(artifact_contract, dict)
        or artifact_contract.get("path") != "artifact-contract.md"
    ):
        raise SoulmateSkillLoadError("Invalid Soulmate artifact contract")
    if (
        artifact_contract.get("formats") != ["zip", "skill"]
        or artifact_contract.get("content_root") != "skills"
    ):
        raise SoulmateSkillLoadError("Invalid Soulmate artifact contract")
    entries = value.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SoulmateSkillLoadError("Soulmate manifest entries must be non-empty")
    ids: set[str] = set()
    sources: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise SoulmateSkillLoadError("Soulmate manifest entry must be an object")
        required = {
            "id",
            "version",
            "owner",
            "kind",
            "source",
            "consumers",
            "compatibility",
            "artifact",
        }
        if not required.issubset(entry):
            raise SoulmateSkillLoadError("Soulmate manifest entry is incomplete")
        skill_id = entry["id"]
        source = entry["source"]
        consumers = entry["consumers"]
        if (
            not isinstance(skill_id, str)
            or not skill_id.startswith("soulmate.")
            or skill_id in ids
        ):
            raise SoulmateSkillLoadError(
                "Soulmate manifest has an invalid or duplicate ID"
            )
        if (
            not isinstance(source, str)
            or not source.endswith(".md")
            or "\\" in source
            or PurePosixPath(source).is_absolute()
            or ".." in PurePosixPath(source).parts
            or "." in PurePosixPath(source).parts
            or source in sources
        ):
            raise SoulmateSkillLoadError(
                "Soulmate manifest has an invalid or duplicate source"
            )
        if (
            not isinstance(entry["version"], str)
            or not entry["version"]
            or not isinstance(entry["compatibility"], str)
            or not entry["compatibility"]
        ):
            raise SoulmateSkillLoadError("Soulmate manifest entry has invalid version")
        if entry["owner"] != "Soulmate" or entry["kind"] != "foundation":
            raise SoulmateSkillLoadError(
                "Soulmate manifest entry has invalid ownership"
            )
        if entry["artifact"] != "soulmate-ai":
            raise SoulmateSkillLoadError("Soulmate manifest entry has invalid artifact")
        if (
            not isinstance(consumers, list)
            or not consumers
            or any(
                not isinstance(consumer, str)
                or consumer not in {"soulmate-only", "soulmap-compatible"}
                for consumer in consumers
            )
            or len(consumers) != len(set(consumers))
        ):
            raise SoulmateSkillLoadError(
                "Soulmate manifest entry has invalid consumers"
            )
        ids.add(skill_id)
        sources.add(source)
    return value


def _select_entry(manifest: dict[str, Any], skill_id: str) -> dict[str, Any]:
    for entry in manifest["entries"]:
        if entry["id"] == skill_id:
            if "soulmap-compatible" not in entry["consumers"]:
                raise SoulmateSkillLoadError(
                    f"Soulmate skill is not approved for SoulMap: {skill_id}"
                )
            return entry
    raise SoulmateSkillLoadError(
        f"Soulmate skill is absent from the manifest: {skill_id}"
    )


def _load_selected_skill(
    manifest: dict[str, Any], reader: _DirectoryContentReader, skill_id: str
) -> LoadedSoulmateSkill:
    entry = _select_entry(manifest, skill_id)
    content = reader.read(entry["source"])
    return _validate_skill_content(entry, content)


def _validate_skill_content(entry: dict[str, Any], content: str) -> LoadedSoulmateSkill:
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        raise SoulmateSkillLoadError(
            f"Soulmate skill has malformed front matter: {entry['source']}"
        )
    return _build_loaded_skill(entry, content)


def _build_loaded_skill(entry: dict[str, Any], content: str) -> LoadedSoulmateSkill:
    if "\x00" in content:
        raise SoulmateSkillLoadError(
            f"Soulmate skill contains a NUL byte: {entry['source']}"
        )
    return LoadedSoulmateSkill(
        id=entry["id"],
        version=entry["version"],
        compatibility=entry["compatibility"],
        source=entry["source"],
        content=content,
    )


__all__ = [
    "SOULMAP_COMPATIBLE_SKILL_IDS",
    "LoadedSoulmateSkill",
    "SoulMapSoulmateAdapter",
    "SoulmateFoundationBundle",
    "SoulmateSkillLoadError",
    "SoulmateSkillLoader",
]
