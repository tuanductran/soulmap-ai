"""Build isolated, deterministic Soulmate AI skill artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "packages" / "soulmate"
SKILLS_ROOT = PACKAGE_ROOT / "skills"
MANIFEST_PATH = SKILLS_ROOT / "manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "soulmate-skills"
ARTIFACT_ZIP_NAME = "soulmate-ai.zip"
ARTIFACT_SKILL_NAME = "soulmate-ai.skill"
MANIFEST_NAME = "manifest.json"
PROVENANCE_NAME = "PROVENANCE.json"
CHECKSUMS_NAME = "SHA256SUMS"
SCHEMA_VERSION = "1.0"
MAX_MANIFEST_ENTRIES = 64
REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "artifact-contract.md",
    "manifest.json",
    "PROVENANCE.json",
)


class SoulmateSkillsBuildError(RuntimeError):
    """Raised when the Soulmate skills artifact cannot be built safely."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SoulmateSkillsBuildError(f"Invalid JSON manifest: {path}") from error
    if not isinstance(value, dict):
        raise SoulmateSkillsBuildError("Soulmate skills manifest must be a JSON object")
    return value


def _safe_relative_source(source: Any) -> str:
    if not isinstance(source, str) or not source.strip():
        raise SoulmateSkillsBuildError(
            "Manifest entry source must be a non-empty string"
        )
    if "\\" in source:
        raise SoulmateSkillsBuildError(f"Manifest source uses backslashes: {source}")
    path = PurePosixPath(source)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise SoulmateSkillsBuildError(
            f"Manifest source escapes the skills root: {source}"
        )
    normalized = path.as_posix()
    if normalized != source or not normalized.endswith(".md"):
        raise SoulmateSkillsBuildError(
            f"Manifest source is not a normalized Markdown path: {source}"
        )
    return normalized


def _validate_entry(entry: Any, *, source_root: Path | None) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise SoulmateSkillsBuildError(
            "Every Soulmate skills manifest entry must be an object"
        )
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
    missing = sorted(required.difference(entry))
    if missing:
        raise SoulmateSkillsBuildError(
            f"Manifest entry is missing fields: {', '.join(missing)}"
        )
    if not isinstance(entry["id"], str) or not entry["id"].startswith("soulmate."):
        raise SoulmateSkillsBuildError(
            "Manifest entry id must use the soulmate. namespace"
        )
    if not isinstance(entry["version"], str) or not entry["version"]:
        raise SoulmateSkillsBuildError(
            f"Manifest entry has an invalid version: {entry['id']}"
        )
    if entry["owner"] != "Soulmate":
        raise SoulmateSkillsBuildError(
            f"Manifest entry has an invalid owner: {entry['id']}"
        )
    if entry["kind"] not in {"foundation", "companion"}:
        raise SoulmateSkillsBuildError(
            f"Manifest entry has an invalid kind: {entry['id']}"
        )
    consumers = entry["consumers"]
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
        raise SoulmateSkillsBuildError(
            f"Manifest entry has an invalid consumer scope: {entry['id']}"
        )
    if entry["artifact"] != "soulmate-ai":
        raise SoulmateSkillsBuildError(
            f"Manifest entry has an invalid artifact: {entry['id']}"
        )
    source = _safe_relative_source(entry["source"])
    if source_root is not None:
        source_path = (source_root / source).resolve()
        if source_path.parent != (source_root / PurePosixPath(source).parent).resolve():
            raise SoulmateSkillsBuildError(
                f"Manifest source escaped the skills root: {source}"
            )
        if not source_path.is_file():
            raise SoulmateSkillsBuildError(
                f"Manifest source file does not exist: {source}"
            )
        _validate_skill_markdown(source_path)
    return {
        "id": entry["id"],
        "version": entry["version"],
        "owner": entry["owner"],
        "kind": entry["kind"],
        "source": source,
        "consumers": list(entry["consumers"]),
        "compatibility": entry["compatibility"],
        "artifact": entry["artifact"],
    }


def _validate_skill_markdown(path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise SoulmateSkillsBuildError(
            f"Skill source is not valid UTF-8 Markdown: {path}"
        ) from error
    if not content.startswith("---\n"):
        raise SoulmateSkillsBuildError(f"Skill source is missing front matter: {path}")
    front_matter, separator, _ = content[4:].partition("\n---\n")
    if not separator:
        raise SoulmateSkillsBuildError(
            f"Skill source has malformed front matter: {path}"
        )
    required_lines = {"name:", "description:", "license:"}
    if not all(
        any(line.startswith(prefix) for line in front_matter.splitlines())
        for prefix in required_lines
    ):
        raise SoulmateSkillsBuildError(
            f"Skill source has incomplete front matter: {path}"
        )
    if "\x00" in content:
        raise SoulmateSkillsBuildError(f"Skill source contains a NUL byte: {path}")


def validate_manifest(
    manifest: dict[str, Any], *, source_root: Path | None = SKILLS_ROOT
) -> list[dict[str, Any]]:
    """Validate a canonical manifest and return normalized entries."""

    required = {
        "schema_version",
        "library_id",
        "display_name",
        "source_of_truth",
        "distribution",
        "artifact_contract",
        "compatibility",
        "entries",
    }
    missing = sorted(required.difference(manifest))
    if missing:
        raise SoulmateSkillsBuildError(
            f"Manifest is missing fields: {', '.join(missing)}"
        )
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise SoulmateSkillsBuildError(
            f"Unsupported manifest schema: {manifest['schema_version']}"
        )
    if manifest["library_id"] != "soulmate-ai":
        raise SoulmateSkillsBuildError("Manifest library_id must be soulmate-ai")
    if manifest["source_of_truth"] != "packages/soulmate/skills":
        raise SoulmateSkillsBuildError(
            "Manifest source_of_truth must be packages/soulmate/skills"
        )
    distribution = manifest["distribution"]
    if (
        not isinstance(distribution, dict)
        or distribution.get("artifact_family") != "soulmate-ai"
    ):
        raise SoulmateSkillsBuildError(
            "Manifest distribution artifact_family must be soulmate-ai"
        )
    if distribution.get("public_registry") is not False:
        raise SoulmateSkillsBuildError(
            "Soulmate skills manifest must remain pre-release"
        )
    artifact_contract = manifest["artifact_contract"]
    if not isinstance(artifact_contract, dict):
        raise SoulmateSkillsBuildError("Manifest artifact_contract must be an object")
    if artifact_contract.get("path") != "artifact-contract.md":
        raise SoulmateSkillsBuildError("Manifest artifact contract path is invalid")
    if artifact_contract.get("formats") != ["zip", "skill"]:
        raise SoulmateSkillsBuildError("Manifest artifact contract formats are invalid")
    if artifact_contract.get("content_root") != "skills":
        raise SoulmateSkillsBuildError(
            "Manifest artifact contract content_root is invalid"
        )
    if artifact_contract.get("required_files") != list(REQUIRED_FILES):
        raise SoulmateSkillsBuildError(
            "Manifest artifact contract required_files are invalid"
        )
    entries = manifest["entries"]
    if (
        not isinstance(entries, list)
        or not entries
        or len(entries) > MAX_MANIFEST_ENTRIES
    ):
        raise SoulmateSkillsBuildError(
            "Manifest entries must be a non-empty bounded list"
        )
    normalized = [_validate_entry(entry, source_root=source_root) for entry in entries]
    ids = [entry["id"] for entry in normalized]
    sources = [entry["source"] for entry in normalized]
    if len(ids) != len(set(ids)):
        raise SoulmateSkillsBuildError("Manifest contains duplicate skill ids")
    if len(sources) != len(set(sources)):
        raise SoulmateSkillsBuildError("Manifest contains duplicate skill sources")
    versions = {entry["version"] for entry in normalized}
    if len(versions) != 1:
        raise SoulmateSkillsBuildError(
            "All current Soulmate skills must share one collection version"
        )
    return normalized


def load_manifest(
    path: Path = MANIFEST_PATH,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = _read_json(path)
    return manifest, validate_manifest(manifest, source_root=path.parent)


def _projection(
    manifest: dict[str, Any], entries: list[dict[str, Any]]
) -> dict[str, Any]:
    version = entries[0]["version"]
    return {
        "schema_version": SCHEMA_VERSION,
        "library_id": manifest["library_id"],
        "display_name": manifest["display_name"],
        "source_of_truth": manifest["source_of_truth"],
        "artifact_family": manifest["distribution"]["artifact_family"],
        "artifact_contract": manifest["artifact_contract"],
        "artifact_version": version,
        "compatibility": manifest["compatibility"],
        "entries": entries,
    }


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    with zipfile.ZipFile(
        buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return buffer.getvalue()


def _provenance(
    projection: dict[str, Any],
    files: dict[str, bytes],
    *,
    source_commit: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "library_id": projection["library_id"],
        "artifact_family": projection["artifact_family"],
        "artifact_version": projection["artifact_version"],
        "manifest_sha256": _sha256_bytes(files[MANIFEST_NAME]),
        "source_commit": source_commit,
        "selected_entries": [entry["id"] for entry in projection["entries"]],
        "file_list": sorted([*files, PROVENANCE_NAME]),
        "build": {
            "builder": "scripts/build_soulmate_skills.py",
            "deterministic": True,
            "zip_metadata": "fixed",
        },
        "verification": {"status": "not-run", "checks": []},
    }


def _write_checksums(output_dir: Path, artifact_paths: list[Path]) -> Path:
    lines = []
    for path in sorted(artifact_paths, key=lambda item: item.name):
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    checksum_path = output_dir / CHECKSUMS_NAME
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def build_artifacts(
    output_dir: Path = DEFAULT_OUTPUT,
    *,
    manifest_path: Path = MANIFEST_PATH,
    package_root: Path = PACKAGE_ROOT,
    source_commit: str | None = None,
) -> tuple[Path, Path, Path, Path, Path]:
    """Build deterministic `.zip` and `.skill` artifacts from an explicit manifest."""

    manifest, entries = load_manifest(manifest_path)
    if package_root.resolve() != PACKAGE_ROOT.resolve():
        skills_root = manifest_path.parent
    else:
        skills_root = SKILLS_ROOT
    output_dir = output_dir.resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    readme = package_root / "README.md"
    license_path = package_root / "LICENSE"
    contract_path = skills_root / manifest["artifact_contract"]["path"]
    skill_entrypoint = skills_root / "SKILL.md"
    if (
        not readme.is_file()
        or not license_path.is_file()
        or not contract_path.is_file()
        or not skill_entrypoint.is_file()
    ):
        raise SoulmateSkillsBuildError(
            "Soulmate package README.md, LICENSE, artifact contract, and SKILL.md are required"
        )
    _validate_skill_markdown(skill_entrypoint)

    files: dict[str, bytes] = {
        "SKILL.md": skill_entrypoint.read_bytes(),
        "README.md": readme.read_bytes(),
        "LICENSE": license_path.read_bytes(),
        "artifact-contract.md": contract_path.read_bytes(),
    }
    projection = _projection(manifest, entries)
    files[MANIFEST_NAME] = _json_bytes(projection)
    for entry in entries:
        source_path = skills_root / entry["source"]
        files[f"skills/{entry['source']}"] = source_path.read_bytes()
    provenance = _provenance(
        projection,
        files,
        source_commit=source_commit or os.getenv("GITHUB_SHA", "local"),
    )
    files[PROVENANCE_NAME] = _json_bytes(provenance)

    artifact_bytes = _zip_bytes(files)
    zip_path = output_dir / ARTIFACT_ZIP_NAME
    skill_path = output_dir / ARTIFACT_SKILL_NAME
    zip_path.write_bytes(artifact_bytes)
    skill_path.write_bytes(artifact_bytes)
    manifest_output = output_dir / MANIFEST_NAME
    provenance_output = output_dir / PROVENANCE_NAME
    manifest_output.write_bytes(files[MANIFEST_NAME])
    provenance_output.write_bytes(files[PROVENANCE_NAME])
    checksum_path = _write_checksums(output_dir, [zip_path, skill_path])
    return zip_path, skill_path, manifest_output, provenance_output, checksum_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--source-commit", default=None)
    args = parser.parse_args(argv)
    artifacts = build_artifacts(
        args.output_dir,
        manifest_path=args.manifest.resolve(),
        source_commit=args.source_commit,
    )
    for artifact in artifacts:
        print(f"OK: {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
