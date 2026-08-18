from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from soulmap.devtools.packaging import library


def _write(root: Path, relative_path: str, content: str = "content\n") -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _catalog() -> str:
    return json.dumps(
        {
            "schema_version": "1.0",
            "library_id": "soulmap-ai",
            "display_name": "SoulMap AI",
            "project_version_source": "pyproject.toml:[project].version",
            "repository": "https://github.com/tuanductran/soulmap-ai",
            "license": "MIT",
            "source_of_truth": {"runtime_manifest": "SKILL.md"},
            "distribution": {"release_url_template": "https://example.test/v{version}"},
            "compatibility": {"root_manifest": "SKILL.md"},
            "entries": [
                {
                    "id": "brand",
                    "plugin_name": "SoulMap Brand System",
                    "path": "skills/brand",
                    "kind": "knowledge-skill",
                    "status": "stable",
                }
            ],
        }
    )


def test_build_library_records_release_and_artifact_integrity(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", '[project]\nversion = "1.2.3"\n')
    _write(tmp_path, "LICENSE")
    _write(tmp_path, "AGENTS.md")
    _write(tmp_path, "SKILL.md")
    _write(tmp_path, "skills/brand/brand-doctrine.md")
    _write(tmp_path, ".claude-plugin/marketplace.json", "{}\n")
    _write(tmp_path, "library/catalog.json", _catalog())

    manifest_path = library.build_library(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["version"] == "1.2.3"
    assert payload["release_url"] == "https://example.test/v1.2.3"
    assert payload["generated_by"] == "uv run soulmap library-manifest"
    assert [artifact["filename"] for artifact in payload["artifacts"]] == [
        "soulmap-ai.zip",
        "soulmap-ai.skill",
    ]

    for artifact in payload["artifacts"]:
        artifact_path = tmp_path / artifact["path"]
        assert artifact["size_bytes"] == artifact_path.stat().st_size
        assert (
            artifact["sha256"] == hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        )

    with zipfile.ZipFile(tmp_path / "dist/soulmap-ai.zip") as archive:
        assert ".claude-plugin/marketplace.json" not in archive.namelist()
    with zipfile.ZipFile(tmp_path / "dist/soulmap-ai.skill") as archive:
        assert ".claude-plugin/marketplace.json" in archive.namelist()


def test_read_catalog_rejects_missing_entry_directory(tmp_path: Path) -> None:
    _write(tmp_path, "library/catalog.json", _catalog())

    try:
        library._read_catalog(tmp_path)
    except ValueError as exc:
        assert "Library entry path is not a directory" in str(exc)
    else:
        raise AssertionError("missing Library entry directory was accepted")
