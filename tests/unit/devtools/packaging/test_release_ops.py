"""Tests for release provenance and health contracts."""

import json
from pathlib import Path

import pytest

from soulmap.devtools.packaging.release_ops import (
    ARTIFACT_NAMES,
    ReleaseOperationsError,
    create_provenance,
    main,
    verify_provenance,
)


def _write_project(root: Path, version: str = "0.11.0") -> None:
    (root / "pyproject.toml").write_text(
        f'[project]\nversion = "{version}"\n', encoding="utf-8"
    )


def _write_artifacts(root: Path) -> None:
    dist = root / "dist"
    dist.mkdir()
    for name in ARTIFACT_NAMES:
        (dist / name).write_bytes(name.encode())


def test_create_provenance_records_commit_and_artifact_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "a" * 40,
    )

    payload = create_provenance(tmp_path, {"status": "pass", "version": "0.11.0"})

    assert payload["source_commit"] == "a" * 40
    assert payload["version"] == "0.11.0"
    assert {item["filename"] for item in payload["artifacts"]} == set(ARTIFACT_NAMES)
    assert all(len(item["sha256"]) == 64 for item in payload["artifacts"])


def test_verify_provenance_accepts_matching_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "b" * 40,
    )
    provenance = create_provenance(tmp_path, {"status": "pass", "version": "0.11.0"})
    path = tmp_path / "dist" / "release-provenance.json"
    path.write_text(json.dumps(provenance), encoding="utf-8")

    assert verify_provenance(tmp_path, path)["status"] == "pass"


def test_verify_provenance_rejects_commit_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "c" * 40,
    )
    path = tmp_path / "dist" / "release-provenance.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": "pass",
                "version": "0.11.0",
                "source_commit": "d" * 40,
                "artifacts": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ReleaseOperationsError, match="source_commit does not match"):
        verify_provenance(tmp_path, path)


def test_verify_provenance_rejects_artifact_hash_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "e" * 40,
    )
    provenance = create_provenance(tmp_path, {"status": "pass", "version": "0.11.0"})
    provenance["artifacts"][0]["sha256"] = "0" * 64
    path = tmp_path / "dist" / "release-provenance.json"
    path.write_text(json.dumps(provenance), encoding="utf-8")

    with pytest.raises(ReleaseOperationsError, match="SHA-256 drift"):
        verify_provenance(tmp_path, path)


def test_create_provenance_rejects_failed_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "f" * 40,
    )

    with pytest.raises(ReleaseOperationsError, match="status must be pass"):
        create_provenance(
            tmp_path, {"status": "fail", "version": "0.11.0"}
        )


def test_create_provenance_rejects_version_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "f" * 40,
    )

    with pytest.raises(ReleaseOperationsError, match=r"must match pyproject.toml"):
        create_provenance(
            tmp_path, {"status": "pass", "version": "0.12.0"}
        )


def test_verify_provenance_rejects_duplicate_artifact_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "a" * 40,
    )
    provenance = create_provenance(
        tmp_path, {"status": "pass", "version": "0.11.0"}
    )
    provenance["artifacts"].append(dict(provenance["artifacts"][0]))
    path = tmp_path / "dist" / "release-provenance.json"
    path.write_text(json.dumps(provenance), encoding="utf-8")

    with pytest.raises(ReleaseOperationsError, match="artifact set is invalid"):
        verify_provenance(tmp_path, path)


def test_verify_provenance_rejects_non_object_json(tmp_path: Path) -> None:
    path = tmp_path / "release-provenance.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(
        ReleaseOperationsError, match="provenance must be a JSON object"
    ):
        verify_provenance(tmp_path, path)


def test_verify_provenance_rejects_unhashable_artifact_filename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops._git",
        lambda root, *args: "a" * 40,
    )
    provenance = create_provenance(
        tmp_path, {"status": "pass", "version": "0.11.0"}
    )
    provenance["artifacts"][0]["filename"] = []
    path = tmp_path / "dist" / "release-provenance.json"
    path.write_text(json.dumps(provenance), encoding="utf-8")

    with pytest.raises(ReleaseOperationsError, match="artifact set is invalid"):
        verify_provenance(tmp_path, path)



def test_provenance_cli_rejects_stale_verification_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_project(tmp_path)
    _write_artifacts(tmp_path)
    verification_path = tmp_path / "dist" / "release-verification.json"
    provenance_path = tmp_path / "dist" / "release-provenance.json"
    verification_path.write_text(
        json.dumps({"status": "pass", "version": "0.11.0"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "soulmap.devtools.packaging.release_ops.verify_release",
        lambda _root: {
            "status": "pass",
            "version": "0.11.0",
            "verified_artifact_count": 3,
        },
    )

    result = main(
        [
            "provenance",
            "--root",
            str(tmp_path),
            "--verification",
            str(verification_path),
            "--provenance",
            str(provenance_path),
        ]
    )

    assert result == 1
    assert not provenance_path.exists()
    assert "does not match the current repository" in capsys.readouterr().err
