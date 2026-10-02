"""Build the versioned SoulMap AI Library distribution manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import tomllib
from pathlib import Path
from typing import Any

from soulmap.devtools.packaging.build_skill import build_skill, build_zip
from soulmap.devtools.support.repo import REPO_ROOT

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")
MANIFEST_NAME = "soulmap-ai-library.json"


def _read_marketplace(repo_root: Path) -> dict[str, Any]:
    """Read the shipped skill inventory from marketplace metadata."""
    path = repo_root / MARKETPLACE_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Marketplace metadata is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Marketplace metadata must contain a JSON object")
    plugins = payload.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError("Marketplace metadata must define at least one plugin")
    for plugin in plugins:
        if not isinstance(plugin, dict):
            raise ValueError("Marketplace plugins must be objects")
        skills = plugin.get("skills")
        if not isinstance(skills, list) or len(skills) != 1:
            raise ValueError(
                "Each marketplace plugin must define exactly one skill path"
            )
        skill_path = skills[0]
        if not isinstance(skill_path, str) or not skill_path.startswith("./"):
            raise ValueError("Marketplace skill paths must be repository-relative")
        path_value = skill_path[2:]
        if not (repo_root / path_value).is_dir():
            raise ValueError(f"Marketplace skill path is not a directory: {path_value}")
    return payload


def _project_version(repo_root: Path) -> str:
    """Read the project version from pyproject.toml."""
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


def _library_entries(marketplace: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize marketplace skills into the Library's public inventory."""
    entries: list[dict[str, Any]] = []
    for plugin in marketplace["plugins"]:
        skill_path = plugin["skills"][0][2:]
        entries.append(
            {
                "id": Path(skill_path).name,
                "plugin_name": plugin["name"],
                "path": skill_path,
                "kind": "knowledge-skill",
                "status": "stable",
            }
        )
    return entries


def build_library(repo_root: Path) -> Path:
    """Build distribution artifacts and write the versioned Library manifest."""
    marketplace = _read_marketplace(repo_root)
    version = _project_version(repo_root)
    zip_path = build_zip(repo_root)
    skill_path = build_skill(repo_root)

    manifest = {
        "schema_version": "1.0",
        "library_id": "soulmap-ai",
        "display_name": "SoulMap AI Library",
        "version": version,
        "repository": "https://github.com/tuanductran/soulmap-ai",
        "project_version_source": "pyproject.toml:[project].version",
        "source_of_truth": {
            "behavioral_contract": "SOULMAP.md",
            "root_skill": "SKILL.md",
            "skill_inventory": ".claude-plugin/marketplace.json",
        },
        "distribution": {
            "catalog_status": "derived-from-shipped-skill-inventory",
            "installation_mode": "manual-upload",
            "automatic_installation": False,
            "release_url_template": "https://github.com/tuanductran/soulmap-ai/releases/tag/v{version}",
        },
        "compatibility": {
            "root_manifest": "SKILL.md",
            "skills_root": "skills",
        },
        "entries": _library_entries(marketplace),
        "release_url": f"https://github.com/tuanductran/soulmap-ai/releases/tag/v{version}",
        "generated_by": "uv run soulmap library-manifest",
        "artifacts": [
            _artifact_metadata(repo_root, zip_path, skill=False),
            _artifact_metadata(repo_root, skill_path, skill=True),
        ],
    }

    output_path = repo_root / "dist" / MANIFEST_NAME
    output_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(f"OK (library): {output_path}")
    return output_path


def main(argv: list[str] | None = None) -> int:
    """Build the versioned Library distribution manifest."""
    parser = argparse.ArgumentParser(
        description="Build the versioned dist/soulmap-ai-library.json manifest."
    )
    parser.parse_args(argv)
    build_library(REPO_ROOT)
    return 0
