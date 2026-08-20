"""Verify Library manifest metadata against generated distribution artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


class ArtifactIntegrityError(ValueError):
    """Raised when a generated artifact disagrees with the Library manifest."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ArtifactIntegrityError(f"manifest not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactIntegrityError(f"manifest is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ArtifactIntegrityError("manifest root must be a JSON object")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ArtifactIntegrityError("manifest must contain a non-empty artifacts list")
    return payload


def verify_artifacts(manifest_path: Path) -> list[dict[str, Any]]:
    """Verify every manifest artifact and return normalized verification results."""
    manifest = _load_manifest(manifest_path)
    repo_root = manifest_path.parent.parent
    results: list[dict[str, Any]] = []

    for artifact in manifest["artifacts"]:
        if not isinstance(artifact, dict):
            raise ArtifactIntegrityError("manifest artifact entries must be objects")
        filename = artifact.get("filename")
        relative_path = artifact.get("path")
        expected_size = artifact.get("size_bytes")
        expected_sha256 = artifact.get("sha256")
        if not isinstance(filename, str) or not isinstance(relative_path, str):
            raise ArtifactIntegrityError(
                "each artifact must define filename, path, size_bytes, and sha256"
            )
        if not isinstance(expected_size, int) or not isinstance(expected_sha256, str):
            raise ArtifactIntegrityError(
                "each artifact must define filename, path, size_bytes, and sha256"
            )

        artifact_path = repo_root / relative_path
        if not artifact_path.is_file():
            raise ArtifactIntegrityError(f"artifact not found: {artifact_path}")
        actual_size = artifact_path.stat().st_size
        actual_sha256 = _sha256(artifact_path)
        if actual_size != expected_size:
            raise ArtifactIntegrityError(
                f"size mismatch for {filename}: expected {expected_size}, got {actual_size}"
            )
        if actual_sha256 != expected_sha256:
            raise ArtifactIntegrityError(
                f"SHA-256 mismatch for {filename}: expected {expected_sha256}, got {actual_sha256}"
            )
        results.append(
            {
                "filename": filename,
                "path": relative_path,
                "size_bytes": actual_size,
                "sha256": actual_sha256,
            }
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify dist artifacts against dist/soulmap-ai-library.json."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("dist/soulmap-ai-library.json"),
        help="Path to the generated Library manifest",
    )
    args = parser.parse_args(argv)
    try:
        results = verify_artifacts(args.manifest)
    except ArtifactIntegrityError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for result in results:
        print(
            f"PASS {result['filename']}: "
            f"{result['size_bytes']} bytes sha256={result['sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
