from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from soulmap.devtools.checks.skills_boundary import audit_text
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
    assert "generated_by" not in payload
    assert "project_version_source" not in payload
    assert (
        audit_text(
            library.MANIFEST_NAME,
            manifest_path.read_text(encoding="utf-8"),
        )
        == []
    )
    assert payload["entries"][0]["path"] == "."
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
    _write(tmp_path, "SKILL.md")
    _write(tmp_path, ".claude-plugin/marketplace.json", _marketplace())

    payload = library._read_marketplace(tmp_path)

    assert payload["name"] == "soulmap-ai"
    assert payload["plugins"][0]["skills"] == ["./"]


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


def test_read_marketplace_rejects_skill_path_traversal(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-skill"
    outside.mkdir()
    payload = json.loads(_marketplace())
    payload["plugins"][0]["skills"] = ["./../outside-skill"]
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="stay inside the repository"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_requires_skill_entrypoint_in_target_directory(
    tmp_path: Path,
) -> None:
    (tmp_path / "skills" / "example").mkdir(parents=True)
    payload = json.loads(_marketplace())
    payload["plugins"][0]["skills"] = ["./skills/example"]
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match=r"must contain SKILL\.md"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_rejects_skill_symlink_that_escapes_repository(
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside-skill"
    outside.mkdir()
    _write(outside, "SKILL.md", "# Outside skill\n")
    skills = tmp_path / "skills"
    skills.mkdir()
    try:
        (skills / "linked").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"directory symlink creation is unavailable: {error}")

    payload = json.loads(_marketplace())
    payload["plugins"][0]["skills"] = ["./skills/linked"]
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="escapes the repository"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_rejects_missing_plugin_name(tmp_path: Path) -> None:
    payload = json.loads(_marketplace())
    payload["plugins"][0].pop("name")
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="plugin names must be non-empty"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_rejects_skill_entrypoint_symlink_outside_repository(
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside-entrypoint"
    _write(outside, "SKILL.md", "# Outside skill\n")
    skills = tmp_path / "skills" / "linked"
    skills.mkdir(parents=True)
    try:
        (skills / "SKILL.md").symlink_to(outside / "SKILL.md")
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"file symlink creation is unavailable: {error}")

    payload = json.loads(_marketplace())
    payload["plugins"][0]["skills"] = ["./skills/linked"]
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="entrypoint must not be a symlink"):
        library._read_marketplace(tmp_path)


def test_read_marketplace_rejects_windows_drive_skill_path(tmp_path: Path) -> None:
    payload = json.loads(_marketplace())
    payload["plugins"][0]["skills"] = ["./C:/outside-skill"]
    _write(tmp_path, ".claude-plugin/marketplace.json", json.dumps(payload))

    with pytest.raises(ValueError, match="must stay inside the repository"):
        library._read_marketplace(tmp_path)
