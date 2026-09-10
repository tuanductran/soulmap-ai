"""Create and verify machine-readable release operational metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from soulmap.devtools.packaging.release_verify import verify_release
from soulmap.devtools.support.repo import REPO_ROOT

ARTIFACT_NAMES = (
    "soulmap-ai.zip",
    "soulmap-ai.skill",
    "soulmap-ai-library.json",
)


class ReleaseOperationsError(ValueError):
    """Raised when release operational metadata is invalid."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _version(repo_root: Path) -> str:
    with (repo_root / "pyproject.toml").open("rb") as handle:
        payload = tomllib.load(handle)
    version = payload.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise ReleaseOperationsError("pyproject.toml must define project.version")
    return version


def create_provenance(repo_root: Path, verification: dict[str, Any]) -> dict[str, Any]:
    """Create provenance linking release version, source commit, and hashes."""
    version = verification.get("version")
    if not isinstance(version, str) or not version:
        raise ReleaseOperationsError("release verification has no version")
    commit = _git(repo_root, "rev-parse", "HEAD")
    timestamp = os.environ.get("RELEASE_TIMESTAMP") or datetime.now(UTC).isoformat()
    artifacts: list[dict[str, Any]] = []
    for name in ARTIFACT_NAMES:
        path = repo_root / "dist" / name
        if not path.is_file():
            raise ReleaseOperationsError(f"release artifact is missing: {name}")
        artifacts.append(
            {
                "filename": name,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return {
        "schema_version": 1,
        "status": "pass",
        "version": version,
        "source_commit": commit,
        "release_timestamp": timestamp,
        "repository": os.environ.get("GITHUB_REPOSITORY", "tuanductran/soulmap-ai"),
        "artifacts": artifacts,
    }


def verify_provenance(repo_root: Path, path: Path) -> dict[str, Any]:
    """Verify provenance against the checked-out release artifacts."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseOperationsError(f"invalid provenance: {exc}") from exc
    if payload.get("schema_version") != 1 or payload.get("status") != "pass":
        raise ReleaseOperationsError("provenance schema/status is invalid")
    version = _version(repo_root)
    if payload.get("version") != version:
        raise ReleaseOperationsError(
            f"provenance version must be {version}, got {payload.get('version', '<missing>')}"
        )
    source_commit = payload.get("source_commit")
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise ReleaseOperationsError("provenance source_commit must be a full Git SHA")
    if source_commit != _git(repo_root, "rev-parse", "HEAD"):
        raise ReleaseOperationsError(
            "provenance source_commit does not match checked-out commit"
        )
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ReleaseOperationsError("provenance artifacts must be a list")
    filenames = {item.get("filename") for item in artifacts if isinstance(item, dict)}
    if filenames != set(ARTIFACT_NAMES):
        raise ReleaseOperationsError("provenance artifact set is invalid")
    for item in artifacts:
        if not isinstance(item, dict):
            raise ReleaseOperationsError("provenance artifact entry is invalid")
        filename = item.get("filename")
        if not isinstance(filename, str):
            raise ReleaseOperationsError("provenance artifact filename is invalid")
        artifact = repo_root / "dist" / filename
        if not artifact.is_file():
            raise ReleaseOperationsError(f"artifact is missing: {artifact.name}")
        if item.get("size_bytes") != artifact.stat().st_size:
            raise ReleaseOperationsError(f"artifact size drift: {artifact.name}")
        if item.get("sha256") != _sha256(artifact):
            raise ReleaseOperationsError(f"artifact SHA-256 drift: {artifact.name}")
    return payload


def main(argv: list[str] | None = None) -> int:
    """Create or verify release operational metadata."""
    parser = argparse.ArgumentParser(
        description="Create or verify SoulMap release operational metadata."
    )
    parser.add_argument("action", choices=("provenance", "health"))
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--verification", type=Path, default=None)
    parser.add_argument("--provenance", type=Path, default=None)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.action == "provenance":
            verification_path = (
                args.verification or root / "dist" / "release-verification.json"
            )
            verification = json.loads(verification_path.read_text(encoding="utf-8"))
            payload = create_provenance(root, verification)
            output = args.provenance or root / "dist" / "release-provenance.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        else:
            verification = verify_release(root)
            provenance_path = (
                args.provenance or root / "dist" / "release-provenance.json"
            )
            provenance = verify_provenance(root, provenance_path)
            payload = {
                "status": "pass",
                "version": verification["version"],
                "provenance": provenance,
            }
        print(json.dumps(payload, indent=2))
        return 0
    except (
        OSError,
        ReleaseOperationsError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as exc:
        print(
            json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
