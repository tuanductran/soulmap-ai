"""Build the versioned SoulMap AI Library manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import tomllib
from copy import deepcopy
from pathlib import Path
from typing import Any

from soulmap.devtools.packaging.build_skill import build_skill, build_zip
from soulmap.devtools.support.repo import REPO_ROOT

CATALOG_PATH = Path("library/catalog.json")
MANIFEST_NAME = "soulmap-ai-library.json"


def _read_catalog(repo_root: Path) -> dict[str, Any]:
    path = repo_root / CATALOG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Library catalog is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Library catalog must contain a JSON object")
    if payload.get("schema_version") != "1.0":
        raise ValueError("Library catalog schema_version must be 1.0")
    if payload.get("library_id") != "soulmap-ai":
        raise ValueError("Library catalog library_id must be soulmap-ai")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Library catalog must define at least one entry")
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Library catalog entries must be objects")
        entry_path = entry.get("path")
        if not isinstance(entry_path, str) or not (repo_root / entry_path).is_dir():
            raise ValueError(f"Library entry path is not a directory: {entry_path}")
    return payload


def _project_version(repo_root: Path) -> str:
    pyproject_path = repo_root / "pyproject.toml"
    with pyproject_path.open("rb") as handle:
        payload = tomllib.load(handle)
    version = payload.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("pyproject.toml must define project.version")
    return version


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_metadata(repo_root: Path, path: Path, *, skill: bool) -> dict[str, Any]:
    return {
        "filename": path.name,
        "path": path.relative_to(repo_root).as_posix(),
        "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "includes_claude_plugin": skill,
    }


def build_library(repo_root: Path) -> Path:
    """Build distribution artifacts and write a versioned Library manifest."""
    catalog = _read_catalog(repo_root)
    version = _project_version(repo_root)
    zip_path = build_zip(repo_root)
    skill_path = build_skill(repo_root)

    manifest = deepcopy(catalog)
    manifest.update(
        {
            "version": version,
            "release_url": catalog["distribution"]["release_url_template"].format(
                version=version
            ),
            "generated_by": "uv run soulmap library-manifest",
            "artifacts": [
                _artifact_metadata(repo_root, zip_path, skill=False),
                _artifact_metadata(repo_root, skill_path, skill=True),
            ],
        }
    )

    output_path = repo_root / "dist" / MANIFEST_NAME
    output_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(f"OK (library): {output_path}")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the versioned dist/soulmap-ai-library.json manifest."
    )
    parser.parse_args(argv)
    build_library(REPO_ROOT)
    return 0
