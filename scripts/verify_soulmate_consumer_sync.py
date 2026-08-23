"""Verify the Soulmate manifest against SoulMap's explicit consumer approval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "packages" / "soulmate" / "skills" / "manifest.json"
DEFAULT_SCOPE = (
    REPO_ROOT
    / "src"
    / "soulmap"
    / "runtime"
    / "knowledge"
    / "soulmate_consumer_scope.json"
)
DEFAULT_PROJECTION = (
    REPO_ROOT
    / "src"
    / "soulmap"
    / "runtime"
    / "knowledge"
    / "_soulmate_consumer_scope.py"
)

SCHEMA_VERSION = "1.0"
EXPECTED_CONSUMER = "soulmap-framework"
EXPECTED_LIBRARY_ID = "soulmate-ai"
EXPECTED_SOURCE_OF_TRUTH = "packages/soulmate/skills"
REQUIRED_SCOPE_KEYS = {
    "schema_version",
    "consumer",
    "library_id",
    "source_of_truth",
    "required_package_compatibility",
    "approved_order",
}
REQUIRED_ENTRY_KEYS = {"id", "version", "compatibility", "source"}


class ConsumerSyncError(ValueError):
    """Raised when the library manifest and consumer approval disagree."""


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConsumerSyncError(f"{label} is not valid UTF-8 JSON: {path}") from error
    if not isinstance(value, dict):
        raise ConsumerSyncError(f"{label} must be a JSON object: {path}")
    return value


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        raise ConsumerSyncError(
            f"{label} keys are invalid (missing={missing}, extra={extra})"
        )


def _validate_scope(scope: dict[str, Any]) -> list[dict[str, str]]:
    _require_exact_keys(scope, REQUIRED_SCOPE_KEYS, "SoulMap consumer scope")
    if scope["schema_version"] != SCHEMA_VERSION:
        raise ConsumerSyncError("Unsupported SoulMap consumer scope schema")
    if scope["consumer"] != EXPECTED_CONSUMER:
        raise ConsumerSyncError("Invalid SoulMap consumer identity")
    if scope["library_id"] != EXPECTED_LIBRARY_ID:
        raise ConsumerSyncError("Invalid SoulMap consumer library identity")
    if scope["source_of_truth"] != EXPECTED_SOURCE_OF_TRUTH:
        raise ConsumerSyncError("Invalid SoulMap consumer source of truth")
    if (
        not isinstance(scope["required_package_compatibility"], str)
        or not scope["required_package_compatibility"]
    ):
        raise ConsumerSyncError("Consumer package compatibility must be non-empty")
    approved = scope["approved_order"]
    if not isinstance(approved, list) or not approved:
        raise ConsumerSyncError("Consumer approved_order must be non-empty")

    entries: list[dict[str, str]] = []
    ids: set[str] = set()
    sources: set[str] = set()
    for index, raw_entry in enumerate(approved):
        if not isinstance(raw_entry, dict):
            raise ConsumerSyncError(
                f"Consumer approved entry {index} must be an object"
            )
        _require_exact_keys(raw_entry, REQUIRED_ENTRY_KEYS, f"Consumer entry {index}")
        if any(
            not isinstance(raw_entry[key], str) or not raw_entry[key]
            for key in REQUIRED_ENTRY_KEYS
        ):
            raise ConsumerSyncError(f"Consumer entry {index} has invalid metadata")
        skill_id = raw_entry["id"]
        source = raw_entry["source"]
        if not skill_id.startswith("soulmate.") or skill_id in ids:
            raise ConsumerSyncError("Consumer scope has an invalid or duplicate ID")
        source_parts = Path(source).parts
        if (
            source in sources
            or not source.endswith(".md")
            or source.startswith("/")
            or "\\" in source
            or ".." in source_parts
            or "." in source_parts
        ):
            raise ConsumerSyncError("Consumer scope has an invalid or duplicate source")
        ids.add(skill_id)
        sources.add(source)
        entries.append({key: raw_entry[key] for key in REQUIRED_ENTRY_KEYS})
    return entries


def _validate_manifest(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ConsumerSyncError("Unsupported Soulmate manifest schema")
    if manifest.get("library_id") != EXPECTED_LIBRARY_ID:
        raise ConsumerSyncError("Invalid Soulmate manifest library identity")
    if manifest.get("source_of_truth") != EXPECTED_SOURCE_OF_TRUTH:
        raise ConsumerSyncError("Invalid Soulmate manifest source of truth")
    distribution = manifest.get("distribution")
    if (
        not isinstance(distribution, dict)
        or distribution.get("public_registry") is not False
    ):
        raise ConsumerSyncError("Soulmate manifest must remain pre-release")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ConsumerSyncError("Soulmate manifest entries must be non-empty")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ConsumerSyncError("Soulmate manifest contains an invalid entry")
        if entry["id"] in by_id:
            raise ConsumerSyncError("Soulmate manifest has a duplicate ID")
        consumers = entry.get("consumers")
        if (
            not isinstance(consumers, list)
            or not consumers
            or len(consumers) != len(set(consumers))
            or any(
                not isinstance(consumer, str)
                or consumer not in {"soulmate-only", "soulmap-compatible"}
                for consumer in consumers
            )
        ):
            raise ConsumerSyncError(
                f"Soulmate manifest has invalid consumers: {entry['id']}"
            )
        by_id[entry["id"]] = entry
    return by_id


def validate_sync(
    manifest: dict[str, Any], scope: dict[str, Any]
) -> list[dict[str, str]]:
    approved = _validate_scope(scope)
    manifest_by_id = _validate_manifest(manifest)
    manifest_compatible = {
        entry_id
        for entry_id, entry in manifest_by_id.items()
        if isinstance(entry.get("consumers"), list)
        and "soulmap-compatible" in entry["consumers"]
    }
    approved_ids = {entry["id"] for entry in approved}
    if manifest_compatible != approved_ids:
        raise ConsumerSyncError(
            "Manifest soulmap-compatible IDs do not exactly match consumer approval"
        )
    manifest_compatible_order = [
        entry_id
        for entry_id, entry in manifest_by_id.items()
        if "soulmap-compatible" in entry["consumers"]
    ]
    if manifest_compatible_order != [entry["id"] for entry in approved]:
        raise ConsumerSyncError(
            "Manifest soulmap-compatible order does not match consumer approval"
        )

    manifest_compatibility = manifest.get("compatibility")
    if not isinstance(manifest_compatibility, dict):
        raise ConsumerSyncError("Soulmate manifest compatibility must be an object")
    package_compatibility = manifest_compatibility.get("soulmate_package")
    if package_compatibility != scope["required_package_compatibility"]:
        raise ConsumerSyncError(
            "Consumer package compatibility does not match manifest"
        )

    for approved_entry in approved:
        manifest_entry = manifest_by_id.get(approved_entry["id"])
        if manifest_entry is None:
            raise ConsumerSyncError(
                f"Approved skill is absent from Soulmate manifest: {approved_entry['id']}"
            )
        if "soulmap-compatible" not in manifest_entry.get("consumers", []):
            raise ConsumerSyncError(
                f"Approved skill is not soulmap-compatible: {approved_entry['id']}"
            )
        if (
            manifest_entry.get("owner") != "Soulmate"
            or manifest_entry.get("kind") != "foundation"
            or manifest_entry.get("artifact") != EXPECTED_LIBRARY_ID
        ):
            raise ConsumerSyncError(
                f"Approved skill is not a Soulmate foundation entry: {approved_entry['id']}"
            )
        for field in REQUIRED_ENTRY_KEYS:
            if manifest_entry.get(field) != approved_entry[field]:
                raise ConsumerSyncError(
                    f"Consumer metadata mismatch for {approved_entry['id']}: {field}"
                )
    return approved


def render_projection(entries: list[dict[str, str]]) -> str:
    lines = [
        '"""Generated by scripts/verify_soulmate_consumer_sync.py; do not edit."""',
        "",
        "APPROVED_SOULMATE_SKILLS = (",
    ]
    for entry in entries:
        lines.extend(
            [
                "    (",
                f"        {json.dumps(entry['id'])},",
                f"        {json.dumps(entry['version'])},",
                f"        {json.dumps(entry['compatibility'])},",
                f"        {json.dumps(entry['source'])},",
                "    ),",
            ]
        )
    lines.extend([")", ""])
    return "\n".join(lines)


def run(
    manifest_path: Path = DEFAULT_MANIFEST,
    scope_path: Path = DEFAULT_SCOPE,
    projection_path: Path = DEFAULT_PROJECTION,
    *,
    write_projection: bool = False,
    report: bool = False,
) -> int:
    try:
        manifest = _read_json(manifest_path, "Soulmate manifest")
        scope = _read_json(scope_path, "SoulMap consumer scope")
        entries = validate_sync(manifest, scope)
        expected_projection = render_projection(entries)
        if write_projection:
            projection_path.write_text(expected_projection, encoding="utf-8")
        elif not projection_path.is_file():
            raise ConsumerSyncError(
                f"Generated projection is missing: {projection_path}"
            )
        elif projection_path.read_text(encoding="utf-8") != expected_projection:
            raise ConsumerSyncError("Generated SoulMap consumer projection is stale")
    except (ConsumerSyncError, OSError, UnicodeDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if report or write_projection:
        print(f"Soulmate/SoulMap consumer sync: {len(entries)} approved skills")
        for index, entry in enumerate(entries, start=1):
            print(f"{index}. {entry['id']} ({entry['version']})")
    else:
        print("PASS: Soulmate manifest and SoulMap consumer scope are synchronized")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    parser.add_argument("--projection", type=Path, default=DEFAULT_PROJECTION)
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--check",
        action="store_true",
        help="check the committed projection (the default action)",
    )
    action_group.add_argument("--write-projection", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args(argv)
    return run(
        manifest_path=args.manifest,
        scope_path=args.scope,
        projection_path=args.projection,
        write_projection=args.write_projection,
        report=args.report,
    )


if __name__ == "__main__":
    raise SystemExit(main())
