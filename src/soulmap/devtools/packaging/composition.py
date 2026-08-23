"""Build the explicit SoulMap-on-Soulmate AI-facing artifacts."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from soulmap.devtools.support.repo import REPO_ROOT

COMPOSITION_SCOPE_PATH = (
    REPO_ROOT
    / "src"
    / "soulmap"
    / "runtime"
    / "knowledge"
    / "soulmate_composition_scope.json"
)
SOULMATE_MANIFEST_PATH = (
    REPO_ROOT / "packages" / "soulmate" / "skills" / "manifest.json"
)
SOULMATE_SKILLS_ROOT = REPO_ROOT / "packages" / "soulmate" / "skills"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "dist" / "soulmap-with-soulmate-ai"
ZIP_NAME = "soulmap-with-soulmate-ai.zip"
SKILL_NAME = "soulmap-with-soulmate-ai.skill"
SCHEMA_VERSION = "1.0"


class CompositionError(RuntimeError):
    """Raised when the composed artifact cannot be built safely."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CompositionError(f"Invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise CompositionError(f"JSON document must be an object: {path}")
    return value


def _safe_source(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise CompositionError("Composition source must be a non-empty string")
    if "\\" in value:
        raise CompositionError(f"Composition source uses backslashes: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or "." in path.parts or ".." in path.parts:
        raise CompositionError(f"Unsafe composition source: {value}")
    normalized = path.as_posix()
    if normalized != value or not normalized.endswith(".md"):
        raise CompositionError(
            f"Composition source is not normalized Markdown: {value}"
        )
    return normalized


def _canonical_entries() -> tuple[dict[str, Any], ...]:
    manifest = _read_json(SOULMATE_MANIFEST_PATH)
    if (
        manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("library_id") != "soulmate-ai"
        or manifest.get("source_of_truth") != "packages/soulmate/skills"
    ):
        raise CompositionError(
            "Soulmate manifest identity or source boundary is invalid"
        )
    distribution = manifest.get("distribution")
    if (
        not isinstance(distribution, dict)
        or distribution.get("artifact_family") != "soulmate-ai"
        or distribution.get("public_registry") is not False
    ):
        raise CompositionError(
            "Soulmate manifest distribution must remain private/pre-release"
        )
    compatibility = manifest.get("compatibility")
    if (
        not isinstance(compatibility, dict)
        or compatibility.get("soulmate_package") != ">=0.1.0,<0.2.0"
    ):
        raise CompositionError("Soulmate package compatibility is invalid")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise CompositionError("Soulmate canonical manifest has no entries")
    result: list[dict[str, Any]] = []
    ids: set[str] = set()
    for raw in entries:
        if not isinstance(raw, dict):
            raise CompositionError("Soulmate manifest entry must be an object")
        required = {"id", "version", "kind", "source", "compatibility", "consumers"}
        if set(raw) < required:
            raise CompositionError(
                f"Soulmate manifest entry is incomplete: {raw.get('id')}"
            )
        skill_id = raw["id"]
        if not isinstance(skill_id, str) or not skill_id.startswith("soulmate."):
            raise CompositionError(f"Invalid Soulmate skill id: {skill_id}")
        if skill_id in ids:
            raise CompositionError(f"Duplicate Soulmate skill id: {skill_id}")
        ids.add(skill_id)
        source = _safe_source(raw["source"])
        if raw["kind"] not in {"foundation", "companion"}:
            raise CompositionError(f"Unsupported Soulmate skill kind: {skill_id}")
        consumers = raw["consumers"]
        if (
            not isinstance(consumers, list)
            or "soulmate-only" not in consumers
            or any(not isinstance(consumer, str) for consumer in consumers)
        ):
            raise CompositionError(
                f"Soulmate skill has invalid consumer metadata: {skill_id}"
            )
        source_path = SOULMATE_SKILLS_ROOT / source
        if not source_path.is_file():
            raise CompositionError(f"Missing Soulmate skill source: {source}")
        result.append(
            {
                "id": skill_id,
                "version": raw["version"],
                "kind": raw["kind"],
                "source": source,
                "compatibility": raw["compatibility"],
            }
        )
    return tuple(result)


def _scope_entries() -> tuple[dict[str, Any], ...]:
    scope = _read_json(COMPOSITION_SCOPE_PATH)
    required = {
        "schema_version",
        "consumer_id",
        "consumer_display_name",
        "library_id",
        "library_version",
        "library_compatibility",
        "source_of_truth",
        "distribution",
        "entries",
    }
    if set(scope) != required:
        raise CompositionError("Composition scope has unknown or missing fields")
    if scope["schema_version"] != SCHEMA_VERSION:
        raise CompositionError("Unsupported composition scope schema")
    if scope["consumer_id"] != "soulmap-with-soulmate-ai":
        raise CompositionError("Invalid composition consumer identity")
    if scope["library_id"] != "soulmate-ai":
        raise CompositionError("Invalid composition library identity")
    if scope["source_of_truth"] != "packages/soulmate/skills":
        raise CompositionError("Invalid composition source boundary")
    distribution = scope["distribution"]
    if (
        not isinstance(distribution, dict)
        or set(distribution) != {"artifact_family", "formats", "status"}
        or distribution["artifact_family"] != "soulmap-with-soulmate-ai"
        or distribution["formats"] != ["zip", "skill"]
        or distribution["status"] != "pre-release"
    ):
        raise CompositionError("Invalid composed artifact distribution metadata")
    raw_entries = scope["entries"]
    if not isinstance(raw_entries, list) or not raw_entries:
        raise CompositionError("Composition scope entries must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in raw_entries:
        if not isinstance(raw, dict) or set(raw) != {
            "id",
            "version",
            "kind",
            "source",
            "compatibility",
        }:
            raise CompositionError("Composition entry has unknown or missing fields")
        skill_id = raw["id"]
        if not isinstance(skill_id, str) or skill_id in seen:
            raise CompositionError(f"Invalid or duplicate composition id: {skill_id}")
        seen.add(skill_id)
        result.append(
            {
                "id": skill_id,
                "version": raw["version"],
                "kind": raw["kind"],
                "source": _safe_source(raw["source"]),
                "compatibility": raw["compatibility"],
            }
        )
    canonical = _canonical_entries()
    manifest = _read_json(SOULMATE_MANIFEST_PATH)
    manifest_compatibility = manifest["compatibility"]
    if scope["library_compatibility"] != manifest_compatibility["soulmate_package"]:
        raise CompositionError(
            "Composition library compatibility does not match canonical manifest"
        )
    if result != list(canonical):
        raise CompositionError(
            "Composition scope must match the canonical Soulmate manifest exactly and in order"
        )
    if scope["library_version"] != canonical[0]["version"]:
        raise CompositionError(
            "Composition library version does not match canonical entries"
        )
    return tuple(result)


def _root_inputs() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for name in ("LICENSE", "AGENTS.md", "SKILL.md"):
        path = REPO_ROOT / name
        if not path.is_file():
            raise CompositionError(f"Missing root SoulMap input: {name}")
        files[name] = path.read_bytes()
    for folder in ("skills", "reference"):
        base = REPO_ROOT / folder
        for path in sorted(base.rglob("*")):
            if path.is_file():
                files[path.relative_to(REPO_ROOT).as_posix()] = path.read_bytes()
    return files


def _composition_skill(root_skill: bytes) -> bytes:
    text = root_skill.decode("utf-8")
    block = """

## Soulmate Library layer

This composed artifact runs the SoulMap Framework on top of the Soulmate Library.
Load the Soulmate foundation and companion skills from `soulmate/` as the reusable
companion layer before composing a response. Soulmate provides transparent AI identity,
presence, reflective listening, emotional attunement, consent, grounded companionship,
human-connection support, repair, and non-dependent closure.

The SoulMap orchestration pipeline remains authoritative for framework selection, crisis
and dependency safety, epistemic guardrails, response shape, voice, and brand. Soulmate
skills do not override SoulMap safety or routing. Do not treat the companion layer as a
human relationship, a conscious person, an oracle, a therapist, or a replacement for
human support. Preserve user agency and make leaving the interaction easy.

### Soulmate foundation skills

Load the relevant files from `soulmate/foundation/` when a reusable contract, lifecycle,
manifest, compatibility, provenance, or validation rule is needed.

### Soulmate companion skills

Load the relevant files from `soulmate/companion/` for identity, presence, listening,
attunement, inquiry, consent, grounded companionship, human connection, repair, or closure.

When the two layers differ, retain the stricter safety boundary and follow the explicit
SoulMap Framework pipeline. The companion layer enriches how SoulMap is present; it does
not replace the Framework.
"""
    return (text.rstrip() + block + "\n").encode("utf-8")


def _projection(entries: tuple[dict[str, Any], ...]) -> bytes:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "consumer_id": "soulmap-with-soulmate-ai",
        "library_id": "soulmate-ai",
        "library_version": entries[0]["version"],
        "artifact_family": "soulmap-with-soulmate-ai",
        "entries": [
            {
                **entry,
                "artifact_path": f"soulmate/{entry['source']}",
            }
            for entry in entries
        ],
    }
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _composition_readme(entries: tuple[dict[str, Any], ...]) -> bytes:
    companions = [entry["id"] for entry in entries if entry["kind"] == "companion"]
    foundations = [entry["id"] for entry in entries if entry["kind"] == "foundation"]
    lines = [
        "# SoulMap AI with Soulmate Library",
        "",
        "This directory is an explicit, build-time composition of Soulmate Library skills into a SoulMap Framework artifact.",
        "",
        "Soulmate remains the reusable companion layer. SoulMap remains the opinionated orchestration, safety, routing, voice, and brand layer.",
        "",
        "The artifact contains the complete reviewed Soulmate skill set. It does not make Soulmate a hidden copy of SoulMap and it does not grant runtime consumer approval.",
        "",
        "## Foundation entries",
        "",
    ]
    lines.extend(f"- `{skill_id}`" for skill_id in foundations)
    lines.extend(["", "## Companion entries", ""])
    lines.extend(f"- `{skill_id}`" for skill_id in companions)
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Load the root `SKILL.md` first. It defines the SoulMap execution pipeline and the precedence relationship. Load files in this directory only when the response needs the reusable Soulmate layer.",
            "",
            "This artifact is pre-release. It is intended for import into an external AI tool and does not host an AI model.",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


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


def _artifact_files(*, include_plugin: bool) -> dict[str, bytes]:
    entries = _scope_entries()
    files = _root_inputs()
    files["SKILL.md"] = _composition_skill(files["SKILL.md"])
    files["soulmate/COMPOSITION.md"] = _composition_readme(entries)
    files["soulmate/manifest.json"] = _projection(entries)
    for entry in entries:
        target = f"soulmate/{entry['source']}"
        files[target] = (SOULMATE_SKILLS_ROOT / entry["source"]).read_bytes()
    if include_plugin:
        plugin_root = REPO_ROOT / ".claude-plugin"
        for path in sorted(plugin_root.rglob("*")):
            if path.is_file():
                files[path.relative_to(REPO_ROOT).as_posix()] = path.read_bytes()
    return files


def build(
    output_dir: Path = DEFAULT_OUTPUT_DIR, *, include_plugin: bool = False
) -> Path:
    name = SKILL_NAME if include_plugin else ZIP_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / name
    output.write_bytes(_zip_bytes(_artifact_files(include_plugin=include_plugin)))
    print(f"OK ({'skill' if include_plugin else 'zip'}): {output}")
    return output


def build_all(output_dir: Path = DEFAULT_OUTPUT_DIR) -> tuple[Path, Path]:
    return build(output_dir), build(output_dir, include_plugin=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build SoulMap AI with Soulmate artifacts"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--skill", action="store_true", help="Build only the .skill artifact"
    )
    args = parser.parse_args(argv)
    if args.skill:
        build(args.output_dir, include_plugin=True)
    else:
        build_all(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
