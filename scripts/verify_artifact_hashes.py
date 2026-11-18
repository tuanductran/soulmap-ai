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


EXPECTED_ARTIFACT_FILENAMES = frozenset({"soulmap-ai.zip", "soulmap-ai.skill"})


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


def _resolve_artifact_path(repo_root: Path, relative_path: str) -> Path:
    """Resolve an artifact path while keeping reads inside the repository."""
    root = repo_root.resolve()
    artifact_path = (root / relative_path).resolve()
    if not artifact_path.is_relative_to(root):
        raise ArtifactIntegrityError(
            f"artifact path escapes repository root: {relative_path}"
        )
    return artifact_path


def verify_artifacts(manifest_path: Path) -> list[dict[str, Any]]:
    """Verify every manifest artifact and return normalized verification results."""
    manifest = _load_manifest(manifest_path)
    repo_root = manifest_path.parent.parent.resolve()
    results: list[dict[str, Any]] = []
    seen_filenames: set[str] = set()

    for artifact in manifest["artifacts"]:
        if not isinstance(artifact, dict):
            raise ArtifactIntegrityError("manifest artifact entries must be objects")
        filename = artifact.get("filename")
        relative_path = artifact.get("path")
        expected_size = artifact.get("size_bytes")
        expected_sha256 = artifact.get("sha256")
        if (
            not all(
                isinstance(value, str) and value.strip()
                for value in (filename, relative_path, expected_sha256)
            )
            or type(expected_size) is not int
            or expected_size < 0
            or len(expected_sha256) != 64
            or any(char not in "0123456789abcdef" for char in expected_sha256.lower())
        ):
            raise ArtifactIntegrityError(
                "each artifact must define a filename, repository-relative path, "
                "non-negative integer size_bytes, and 64-character SHA-256 digest"
            )

        if filename not in EXPECTED_ARTIFACT_FILENAMES:
            raise ArtifactIntegrityError(f"unexpected artifact filename: {filename}")
        if filename in seen_filenames:
            raise ArtifactIntegrityError(f"duplicate artifact filename: {filename}")
        seen_filenames.add(filename)
        artifact_path = _resolve_artifact_path(repo_root, relative_path)
        expected_path = f"dist/{filename}"
        if relative_path != expected_path:
            raise ArtifactIntegrityError(
                f"artifact path for {filename} must be {expected_path}, "
                f"got {relative_path}"
            )
        if not artifact_path.is_file():
            raise ArtifactIntegrityError(f"artifact not found: {artifact_path}")
        actual_size = artifact_path.stat().st_size
        actual_sha256 = _sha256(artifact_path)
        if actual_size != expected_size:
            raise ArtifactIntegrityError(
                f"size mismatch for {filename}: expected {expected_size}, got {actual_size}"
            )
        if actual_sha256 != expected_sha256.lower():
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
    missing_filenames = EXPECTED_ARTIFACT_FILENAMES - seen_filenames
    if missing_filenames:
        raise ArtifactIntegrityError(
            f"manifest is missing expected artifacts: {sorted(missing_filenames)}"
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
