from __future__ import annotations

import json
import tomllib
import zipfile
from pathlib import Path

from soulmap.devtools.packaging import build_skill

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def _read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_marketplace_declares_one_root_skill() -> None:
    marketplace = _read_json(MARKETPLACE)
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        project_version = tomllib.load(handle)["project"]["version"]

    assert marketplace["name"] == "soulmap-ai"
    assert marketplace["version"] == project_version
    assert len(marketplace["plugins"]) == 1

    plugin = marketplace["plugins"][0]
    assert plugin["name"] == "SoulMap AI"
    assert plugin["source"] == "./"
    assert plugin["version"] == marketplace["version"]
    assert plugin["skills"] == ["./"]
    assert (REPO_ROOT / "SKILL.md").is_file()


def test_skill_source_contains_exactly_one_skill_entrypoint() -> None:
    skill_files = [
        path
        for path in build_skill._iter_inputs(REPO_ROOT)
        if path.name == "SKILL.md"
    ]
    assert skill_files == [REPO_ROOT / "SKILL.md"]


def test_skill_archive_contains_exactly_one_skill_entrypoint() -> None:
    artifact = build_skill.build_skill(REPO_ROOT)
    with zipfile.ZipFile(artifact) as archive:
        skill_files = [
            name for name in archive.namelist() if Path(name).name == "SKILL.md"
        ]
    assert skill_files == ["SKILL.md"]


def test_library_documentation_and_source_of_truth_paths_exist() -> None:
    assert (REPO_ROOT / "docs/operations/LIBRARY.md").is_file()
    assert (REPO_ROOT / "docs/operations/UPLOAD.md").is_file()
    assert (REPO_ROOT / "SKILL.md").is_file()
    assert (REPO_ROOT / "SOULMAP.md").is_file()
