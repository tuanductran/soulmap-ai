from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from soulmap import cli as cli_tool
from soulmap.devtools.packaging import build_skill as build_tool
from soulmap.devtools.packaging import dev as dev_tool


def _write(root: Path, relative_path: str, content: str = "content\n") -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _archive_names(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        return set(archive.namelist())


def test_distignore_loader_handles_missing_comments_and_patterns(
    tmp_path: Path,
) -> None:
    assert build_tool._load_distignore(tmp_path) == []

    _write(
        tmp_path,
        ".distignore",
        "# internal files\n\nskills/private.md\n*.tmp\n"
        ".claude-plugin/README.md\n",
    )

    assert build_tool._load_distignore(tmp_path) == [
        "skills/private.md",
        "*.tmp",
        ".claude-plugin/README.md",
    ]
    assert build_tool._is_ignored("skills/private.md", ["skills/private.md"])
    assert build_tool._is_ignored("notes.tmp", ["*.tmp"])
    assert build_tool._is_ignored(
        ".claude-plugin/README.md", [".claude-plugin/README.md"]
    )
    assert not build_tool._is_ignored("skills/public.md", ["*.tmp"])


def _create_source_tree(root: Path) -> set[str]:
    _write(root, "LICENSE")
    _write(root, "SOULMAP.md")
    _write(root, "SKILL.md")
    _write(root, "skills/public.md")
    _write(root, "skills/private.md")
    _write(root, "src/soulmap/runtime/source_registry.py", "REGISTRY = {}\n")
    _write(root, "templates/internal.md")
    _write(root, ".claude-plugin/marketplace.json", "{}\n")
    _write(root, ".claude-plugin/README.md", "Claude plugin development notes\n")
    _write(
        root,
        ".distignore",
        "skills/private.md\n.claude-plugin/README.md\n",
    )
    return {"LICENSE", "SOULMAP.md", "SKILL.md", "skills/public.md"}


def test_build_archives_respect_shipped_and_skill_only_boundaries(
    tmp_path: Path,
) -> None:
    core_names = _create_source_tree(tmp_path)

    zip_path = build_tool.build_zip(tmp_path)
    skill_path = build_tool.build_skill(tmp_path)

    assert not any(
        name.startswith("src/soulmap/runtime/") for name in _archive_names(zip_path)
    )
    assert _archive_names(zip_path) == core_names
    skill_names = _archive_names(skill_path)
    assert skill_names == {
        *core_names,
        ".claude-plugin/marketplace.json",
    }
    assert ".claude-plugin/README.md" not in skill_names


def test_build_all_creates_both_archives(tmp_path: Path) -> None:
    _create_source_tree(tmp_path)

    zip_path, skill_path = build_tool.build_all(tmp_path)

    assert zip_path.name == "soulmap-ai.zip"
    assert skill_path.name == "soulmap-ai.skill"
    assert zip_path.is_file()
    assert skill_path.is_file()


def test_build_cli_always_builds_both_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[Path] = []
    monkeypatch.setattr(build_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        build_tool,
        "build_all",
        lambda root: (
            calls.append(root)
            or (root / "dist/soulmap-ai.zip", root / "dist/soulmap-ai.skill")
        ),
    )

    assert build_tool.main([]) == 0
    assert calls == [tmp_path]
    with pytest.raises(SystemExit):
        build_tool.main(["--skill"])


def test_dev_builds_verifies_and_extracts_both_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create_source_tree(tmp_path)
    monkeypatch.setattr(dev_tool, "REPO_ROOT", tmp_path)

    assert dev_tool.main([]) == 0

    zip_tree = tmp_path / ".soulmap/zip"
    skill_tree = tmp_path / ".soulmap/skill"
    assert _archive_names(tmp_path / "dist/soulmap-ai.zip") == {
        "LICENSE",
        "SOULMAP.md",
        "SKILL.md",
        "skills/public.md",
    }
    assert (zip_tree / "skills/public.md").read_text(encoding="utf-8") == "content\n"
    assert not (zip_tree / ".claude-plugin").exists()
    assert (skill_tree / ".claude-plugin/marketplace.json").is_file()
    assert not (skill_tree / ".claude-plugin/README.md").exists()


def test_dev_rejects_unsafe_archive_member_paths(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.txt", "unsafe")

    with pytest.raises(ValueError, match="unsafe member paths"):
        dev_tool._verify_archive(archive_path, {"../outside.txt"}, tmp_path)


def test_build_zip_replaces_an_existing_archive(tmp_path: Path) -> None:
    _write(tmp_path, "LICENSE")
    first_archive = build_tool.build_zip(tmp_path)
    first_archive.write_text("not a zip", encoding="utf-8")

    rebuilt_archive = build_tool.build_zip(tmp_path)

    assert rebuilt_archive == first_archive
    assert zipfile.is_zipfile(rebuilt_archive)
    assert _archive_names(rebuilt_archive) == {"LICENSE"}


def test_dev_rejects_archive_content_that_differs_from_source(tmp_path: Path) -> None:
    source = _write(tmp_path, "skills/example.md", "current source\n")
    archive_path = tmp_path / "stale.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("skills/example.md", "stale content\n")

    with pytest.raises(ValueError, match="differs from source"):
        dev_tool._verify_archive(
            archive_path, {source.relative_to(tmp_path).as_posix()}, tmp_path
        )


def test_cli_exposes_build_and_dev_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        cli_tool.build_skill,
        "main",
        lambda args: calls.append(("build", args)) or 0,
    )
    monkeypatch.setattr(
        cli_tool.dev_tool,
        "main",
        lambda args: calls.append(("dev", args)) or 0,
    )

    assert cli_tool.main(["build"]) == 0
    assert cli_tool.main(["dev"]) == 0
    assert calls == [("build", []), ("dev", [])]
