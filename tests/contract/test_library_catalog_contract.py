from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG = REPO_ROOT / "library" / "catalog.json"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_library_catalog_matches_marketplace_plugin_paths() -> None:
    catalog = _read_json(CATALOG)
    marketplace = _read_json(MARKETPLACE)

    assert catalog["schema_version"] == "1.0"
    assert catalog["library_id"] == "soulmap-ai"
    assert catalog["project_version_source"] == "pyproject.toml:[project].version"
    assert catalog["distribution"]["catalog_status"] == "versioned-source-catalog"
    assert catalog["distribution"]["installation_mode"] == "manual-upload"
    assert catalog["distribution"]["automatic_installation"] is False
    assert "{version}" in catalog["distribution"]["release_url_template"]

    entries = {entry["id"]: entry for entry in catalog["entries"]}
    assert set(entries) == {
        "brand",
        "frameworks",
        "safety",
        "meta",
        "spiritual",
        "voice",
        "soulmate",
        "writing",
    }

    plugins = {plugin["name"]: plugin for plugin in marketplace["plugins"]}
    assert len(plugins) == len(entries)
    for entry in entries.values():
        path = REPO_ROOT / entry["path"]
        assert path.is_dir()
        plugin = plugins[entry["plugin_name"]]
        assert plugin["source"] == "./"
        assert plugin["skills"] == [f"./{entry['path']}"]


def test_library_documentation_and_source_of_truth_paths_exist() -> None:
    catalog = _read_json(CATALOG)
    for path_value in catalog["source_of_truth"].values():
        assert (REPO_ROOT / path_value).exists()

    assert (REPO_ROOT / "docs/operations/LIBRARY.md").is_file()
    assert (REPO_ROOT / "docs/operations/UPLOAD.md").is_file()
    assert (REPO_ROOT / "SKILL.md").is_file()
    assert (REPO_ROOT / "SOULMAP.md").is_file()
