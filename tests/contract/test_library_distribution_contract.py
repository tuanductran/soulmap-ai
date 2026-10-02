from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_marketplace_skill_inventory_is_complete() -> None:
    marketplace = _read_json(MARKETPLACE)
    plugins = {plugin["name"]: plugin for plugin in marketplace["plugins"]}

    assert marketplace["name"] == "soulmap-ai"
    assert marketplace["version"] == "0.13.0"
    assert set(plugins) == {
        "SoulMap Brand System",
        "SoulMap Core Frameworks",
        "SoulMap Safety Guardrails",
        "SoulMap Meta Guidance",
        "SoulMap Spiritual Layer",
        "SoulMap Voice System",
        "SoulMap Soulmate Layer",
        "SoulMap Writing Layer",
    }

    for plugin in plugins.values():
        assert plugin["source"] == "./"
        assert len(plugin["skills"]) == 1
        path = REPO_ROOT / plugin["skills"][0][2:]
        assert path.is_dir()
        assert (path / "SKILL.md").is_file()


def test_library_documentation_and_source_of_truth_paths_exist() -> None:
    assert (REPO_ROOT / "docs/operations/LIBRARY.md").is_file()
    assert (REPO_ROOT / "docs/operations/UPLOAD.md").is_file()
    assert (REPO_ROOT / "SKILL.md").is_file()
    assert (REPO_ROOT / "SOULMAP.md").is_file()
