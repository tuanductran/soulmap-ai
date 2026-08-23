import copy
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from scripts.build_soulmate_skills import build_artifacts
from scripts.verify_soulmate_consumer_sync import (
    DEFAULT_MANIFEST,
    DEFAULT_PROJECTION,
    DEFAULT_SCOPE,
    ConsumerSyncError,
    render_projection,
    run,
    validate_sync,
)
from soulmap.runtime.knowledge import SOULMAP_COMPATIBLE_SKILL_IDS
from soulmap.runtime.knowledge._soulmate_consumer_scope import (
    APPROVED_SOULMATE_SKILLS,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _valid_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    return _read_json(DEFAULT_MANIFEST), _read_json(DEFAULT_SCOPE)


def _write_inputs(
    tmp_path: Path,
    manifest: dict[str, Any],
    scope: dict[str, Any],
    projection: str | None = None,
) -> tuple[Path, Path, Path]:
    manifest_path = tmp_path / "manifest.json"
    scope_path = tmp_path / "scope.json"
    projection_path = tmp_path / "projection.py"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    scope_path.write_text(
        json.dumps(scope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if projection is not None:
        projection_path.write_text(projection, encoding="utf-8")
    return manifest_path, scope_path, projection_path


def test_valid_manifest_scope_and_projection_are_synchronized() -> None:
    manifest, scope = _valid_inputs()

    approved = validate_sync(manifest, scope)

    assert [entry["id"] for entry in approved] == list(SOULMAP_COMPATIBLE_SKILL_IDS)
    assert (
        tuple(entry[0] for entry in APPROVED_SOULMATE_SKILLS)
        == SOULMAP_COMPATIBLE_SKILL_IDS
    )
    assert render_projection(approved) == DEFAULT_PROJECTION.read_text(encoding="utf-8")
    assert run() == 0


def test_scope_add_and_revoke_are_fail_closed() -> None:
    manifest, scope = _valid_inputs()
    lifecycle = next(
        entry for entry in manifest["entries"] if entry["id"].endswith(".lifecycle")
    )

    added = copy.deepcopy(scope)
    added["approved_order"].append(
        {key: lifecycle[key] for key in ("id", "version", "compatibility", "source")}
    )
    with pytest.raises(ConsumerSyncError, match="exactly match"):
        validate_sync(manifest, added)

    revoked = copy.deepcopy(scope)
    revoked["approved_order"].pop()
    with pytest.raises(ConsumerSyncError, match="exactly match"):
        validate_sync(manifest, revoked)


def test_manifest_approval_drift_is_fail_closed() -> None:
    manifest, scope = _valid_inputs()

    revoked = copy.deepcopy(manifest)
    revoked["entries"][0]["consumers"] = ["soulmate-only"]
    with pytest.raises(ConsumerSyncError, match="exactly match"):
        validate_sync(revoked, scope)

    added = copy.deepcopy(manifest)
    added["entries"][5]["consumers"] = ["soulmate-only", "soulmap-compatible"]
    with pytest.raises(ConsumerSyncError, match="exactly match"):
        validate_sync(added, scope)


def test_id_source_version_and_compatibility_drift_are_rejected() -> None:
    manifest, scope = _valid_inputs()
    cases = (
        ("id", "other-id", "invalid or duplicate ID"),
        ("source", "foundation/other.md", "metadata mismatch"),
        ("version", "9.9.9", "metadata mismatch"),
        ("compatibility", ">=9.0.0,<10.0.0", "metadata mismatch"),
    )

    for field, value, expected in cases:
        changed = copy.deepcopy(scope)
        changed["approved_order"][0][field] = value
        with pytest.raises(ConsumerSyncError, match=expected):
            validate_sync(manifest, changed)


def test_order_and_unknown_consumer_drift_are_rejected() -> None:
    manifest, scope = _valid_inputs()

    reordered = copy.deepcopy(scope)
    reordered["approved_order"][0], reordered["approved_order"][1] = (
        reordered["approved_order"][1],
        reordered["approved_order"][0],
    )
    with pytest.raises(ConsumerSyncError, match="order"):
        validate_sync(manifest, reordered)

    unknown_scope = copy.deepcopy(scope)
    unknown_scope["consumer"] = "unknown-consumer"
    with pytest.raises(ConsumerSyncError, match="identity"):
        validate_sync(manifest, unknown_scope)

    unknown_manifest = copy.deepcopy(manifest)
    unknown_manifest["entries"][0]["consumers"] = ["soulmate-only", "unknown"]
    with pytest.raises(ConsumerSyncError, match="invalid consumers"):
        validate_sync(unknown_manifest, scope)


def test_scope_unknown_fields_and_malformed_json_fail_closed(tmp_path: Path) -> None:
    manifest, scope = _valid_inputs()
    scope["unexpected"] = True
    manifest_path, scope_path, projection_path = _write_inputs(
        tmp_path, manifest, scope
    )
    projection_path.write_text(
        DEFAULT_PROJECTION.read_text(encoding="utf-8"), encoding="utf-8"
    )

    assert (
        run(
            manifest_path=manifest_path,
            scope_path=scope_path,
            projection_path=projection_path,
        )
        == 1
    )

    scope_path.write_text("{malformed", encoding="utf-8")
    assert (
        run(
            manifest_path=manifest_path,
            scope_path=scope_path,
            projection_path=projection_path,
        )
        == 1
    )


def test_stale_generated_projection_is_rejected(tmp_path: Path) -> None:
    manifest, scope = _valid_inputs()
    stale = DEFAULT_PROJECTION.read_text(encoding="utf-8") + "# stale\n"
    manifest_path, scope_path, projection_path = _write_inputs(
        tmp_path, manifest, scope, stale
    )

    assert (
        run(
            manifest_path=manifest_path,
            scope_path=scope_path,
            projection_path=projection_path,
        )
        == 1
    )


def test_soulmate_artifact_excludes_soulmap_approval_files(tmp_path: Path) -> None:
    zip_path, skill_path, _, _, _ = build_artifacts(tmp_path / "artifacts")

    for artifact_path in (zip_path, skill_path):
        with zipfile.ZipFile(artifact_path) as archive:
            names = set(archive.namelist())
        assert "soulmate_consumer_scope.json" not in names
        assert "_soulmate_consumer_scope.py" not in names
        assert all("soulmap" not in name.lower() for name in names)


def test_runtime_approval_ids_are_projection_defined_only() -> None:
    assert (
        tuple(entry[0] for entry in APPROVED_SOULMATE_SKILLS)
        == SOULMAP_COMPATIBLE_SKILL_IDS
    )
    assert "soulmate.foundation.lifecycle" not in SOULMAP_COMPATIBLE_SKILL_IDS
