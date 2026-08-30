from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

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
    _write(tmp_path, "SOULMAP.md")
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

    with pytest.raises(ValueError, match="Library entry path is not a directory"):
        library._read_catalog(tmp_path)


def _catalog_with(**overrides: object) -> str:
    payload = json.loads(_catalog())
    payload.update(overrides)
    return json.dumps(payload)


def test_read_catalog_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Library catalog is missing"):
        library._read_catalog(tmp_path)


def test_read_catalog_rejects_a_non_object_payload(tmp_path: Path) -> None:
    _write(tmp_path, "library/catalog.json", json.dumps(["not", "an", "object"]))

    with pytest.raises(ValueError, match="must contain a JSON object"):
        library._read_catalog(tmp_path)


@pytest.mark.parametrize("schema_version", ["2.0", "1", "", None])
def test_read_catalog_rejects_an_unsupported_schema_version(
    tmp_path: Path, schema_version: object
) -> None:
    """The manifest format is versioned, so an unknown version must not build.

    Emitting a manifest from a catalog this code does not understand would
    ship distribution metadata that silently misdescribes the artifacts.
    """
    _write(
        tmp_path,
        "library/catalog.json",
        _catalog_with(schema_version=schema_version),
    )

    with pytest.raises(ValueError, match=r"schema_version must be 1\.0"):
        library._read_catalog(tmp_path)


def test_read_catalog_rejects_a_foreign_library_id(tmp_path: Path) -> None:
    _write(tmp_path, "library/catalog.json", _catalog_with(library_id="other-project"))

    with pytest.raises(ValueError, match="library_id must be soulmap-ai"):
        library._read_catalog(tmp_path)


@pytest.mark.parametrize("entries", [[], "not a list", None])
def test_read_catalog_requires_at_least_one_entry(
    tmp_path: Path, entries: object
) -> None:
    _write(tmp_path, "library/catalog.json", _catalog_with(entries=entries))

    with pytest.raises(ValueError, match="at least one entry"):
        library._read_catalog(tmp_path)


def test_read_catalog_rejects_a_non_object_entry(tmp_path: Path) -> None:
    _write(tmp_path, "library/catalog.json", _catalog_with(entries=["skills/brand"]))

    with pytest.raises(ValueError, match="entries must be objects"):
        library._read_catalog(tmp_path)


def test_read_catalog_accepts_a_valid_catalog(tmp_path: Path) -> None:
    _write(tmp_path, "library/catalog.json", _catalog())
    _write(tmp_path, "skills/brand/brand-doctrine.md")

    payload = library._read_catalog(tmp_path)

    assert payload["library_id"] == "soulmap-ai"
    assert len(payload["entries"]) == 1


@pytest.mark.parametrize(
    "pyproject",
    [
        "[project]\nname = 'x'\n",
        "[project]\nversion = ''\n",
        "[project]\nversion = 1\n",
    ],
)
def test_project_version_requires_a_non_empty_string(
    tmp_path: Path, pyproject: str
) -> None:
    _write(tmp_path, "pyproject.toml", pyproject)

    with pytest.raises(ValueError, match=r"must define project\.version"):
        library._project_version(tmp_path)


def test_main_builds_the_manifest_for_the_repository(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The command-line entry point builds against the resolved repo root."""
    called: list[Path] = []

    def fake_build_library(repo_root: Path) -> Path:
        called.append(repo_root)
        return tmp_path / "dist" / library.MANIFEST_NAME

    monkeypatch.setattr(library, "build_library", fake_build_library)
    monkeypatch.setattr(library, "REPO_ROOT", tmp_path)

    assert library.main([]) == 0
    assert called == [tmp_path]
