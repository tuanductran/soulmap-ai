from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "verify_artifact_hashes.py"


def _write_manifest(
    tmp_path: Path, *, artifact_content: str = "artifact\n"
) -> tuple[Path, Path]:
    dist = tmp_path / "dist"
    dist.mkdir()
    artifact = dist / "soulmap-ai.zip"
    artifact.write_text(artifact_content, encoding="utf-8")
    raw = artifact.read_bytes()
    manifest = {
        "schema_version": "1.0",
        "library_id": "soulmap-ai",
        "version": "0.8.0",
        "artifacts": [
            {
                "filename": artifact.name,
                "path": "dist/soulmap-ai.zip",
                "size_bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        ],
    }
    manifest_path = dist / "soulmap-ai-library.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path, artifact


def _run(manifest_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest", str(manifest_path)],
        check=False,
        capture_output=True,
        text=True,
    )


def _replace_artifact_path(manifest_path: Path, path: str) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["path"] = path
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_verifier_accepts_matching_artifact(tmp_path: Path) -> None:
    manifest_path, _ = _write_manifest(tmp_path)

    result = _run(manifest_path)

    assert result.returncode == 0
    assert "PASS soulmap-ai.zip" in result.stdout
    assert result.stderr == ""


def test_verifier_accepts_uppercase_sha256_digest(tmp_path: Path) -> None:
    manifest_path, _ = _write_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["sha256"] = manifest["artifacts"][0]["sha256"].upper()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = _run(manifest_path)

    assert result.returncode == 0
    assert "PASS soulmap-ai.zip" in result.stdout


def test_verifier_rejects_tampered_artifact(tmp_path: Path) -> None:
    manifest_path, artifact = _write_manifest(tmp_path)
    artifact.write_text("tampered\n", encoding="utf-8")

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "SHA-256 mismatch for soulmap-ai.zip" in result.stderr


def test_verifier_rejects_missing_artifact(tmp_path: Path) -> None:
    manifest_path, artifact = _write_manifest(tmp_path)
    artifact.unlink()

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "artifact not found" in result.stderr


def test_verifier_rejects_invalid_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "dist" / "soulmap-ai-library.json"
    manifest_path.parent.mkdir()
    manifest_path.write_text("not-json", encoding="utf-8")

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "manifest is not valid JSON" in result.stderr


def test_verifier_rejects_parent_directory_traversal(tmp_path: Path) -> None:
    manifest_path, _ = _write_manifest(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside.zip"
    outside.write_text("outside\n", encoding="utf-8")
    _replace_artifact_path(manifest_path, f"../{outside.name}")

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "artifact path escapes repository root" in result.stderr


def test_verifier_rejects_absolute_artifact_path(tmp_path: Path) -> None:
    manifest_path, _ = _write_manifest(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-absolute.zip"
    outside.write_text("outside\n", encoding="utf-8")
    _replace_artifact_path(manifest_path, str(outside))

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "artifact path escapes repository root" in result.stderr


def test_verifier_rejects_symlink_that_escapes_repository(tmp_path: Path) -> None:
    manifest_path, _ = _write_manifest(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-symlink.zip"
    outside.write_text("outside\n", encoding="utf-8")
    link = manifest_path.parent / "external.zip"
    link.symlink_to(outside)
    _replace_artifact_path(manifest_path, "dist/external.zip")

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "artifact path escapes repository root" in result.stderr


def test_verifier_rejects_invalid_artifact_metadata(tmp_path: Path) -> None:
    manifest_path, _ = _write_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["size_bytes"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = _run(manifest_path)

    assert result.returncode == 1
    assert "non-negative integer size_bytes" in result.stderr
