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


def _marketplace() -> str:
    return json.dumps(
        {
            "name": "soulmap-ai",
            "version": "1.2.3",
            "plugins": [
                {
                    "name": "SoulMap AI",
                    "source": "./",
                    "skills": ["./"],
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
    _write(tmp_path, ".claude-plugin/marketplace.json", _marketplace())

    manifest_path = library.build_library(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["version"] == "1.2.3"
    assert payload["library_id"] == "soulmap-ai"
    assert (
        payload["release_url"]
        == "https://github.com/tuanductran/soulmap-ai/releases/tag/v1.2.3"
    )
    assert payload["generated_by"] == "uv run soulmap library-manifest"
    assert payload["entries"][0]["path"] == "skills/brand"
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


def test_read_marketplace_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Marketplace metadata is missing"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_rejects_a_non_object_payload(tmp_path: Path) -> None:
    _write(
        tmp_path, ".claude-plugin/marketplace.json", json.dumps(["not", "an", "object"])
    )

    with pytest.raises(ValueError, match="must contain a JSON object"):
        library._read_marketplace(tmp_path)


@pytest.mark.parametrize("plugins", [[], "not a list", None])
def test_read_marketplace_requires_plugins(tmp_path: Path, plugins: object) -> None:
    payload = json.loads(_marketplace())
    payload["plugins"] = plugins
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="at least one plugin"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_rejects_invalid_skill_path(tmp_path: Path) -> None:
    payload = json.loads(_marketplace())
    payload["plugins"][0]["skills"] = ["skills/brand"]
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="repository-relative"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_accepts_valid_inventory(tmp_path: Path) -> None:
    _write(tmp_path, ".claude-plugin/marketplace.json", _marketplace())
    _write(tmp_path, "skills/brand/brand-doctrine.md")

    payload = library._read_marketplace(tmp_path)

    assert payload["name"] == "soulmap-ai"
    assert payload["plugins"][0]["skills"] == ["./skills/brand"]


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
    called: list[Path] = []

    def fake_build_library(repo_root: Path) -> Path:
        called.append(repo_root)
        return tmp_path / "dist" / library.MANIFEST_NAME

    monkeypatch.setattr(library, "build_library", fake_build_library)
    monkeypatch.setattr(library, "REPO_ROOT", tmp_path)

    assert library.main([]) == 0
    assert called == [tmp_path]
