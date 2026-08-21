from __future__ import annotations

import zipfile
from pathlib import Path

from soulmap.devtools.packaging import build_skill as build_tool


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

    _write(tmp_path, ".distignore", "# internal files\n\nskills/private.md\n*.tmp\n")

    assert build_tool._load_distignore(tmp_path) == ["skills/private.md", "*.tmp"]
    assert build_tool._is_ignored("skills/private.md", ["skills/private.md"])
    assert build_tool._is_ignored("notes.tmp", ["*.tmp"])
    assert not build_tool._is_ignored("skills/public.md", ["*.tmp"])


def test_build_archives_respect_shipped_and_skill_only_boundaries(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "LICENSE")
    _write(tmp_path, "AGENTS.md")
    _write(tmp_path, "SKILL.md")
    _write(tmp_path, "skills/public.md")
    _write(tmp_path, "skills/private.md")
    _write(tmp_path, "reference/languages/vi/spiritual-bypass.md")
    _write(tmp_path, "templates/internal.md")
    _write(tmp_path, ".claude-plugin/marketplace.json", "{}\n")
    _write(tmp_path, ".distignore", "skills/private.md\n")

    zip_path = build_tool.build_zip(tmp_path)
    skill_path = build_tool.build_skill(tmp_path)

    core_names = {
        "LICENSE",
        "AGENTS.md",
        "SKILL.md",
        "skills/public.md",
        "reference/languages/vi/spiritual-bypass.md",
    }
    assert _archive_names(zip_path) == core_names
    assert _archive_names(skill_path) == {
        *core_names,
        ".claude-plugin/marketplace.json",
    }


def test_build_zip_replaces_an_existing_archive(tmp_path: Path) -> None:
    _write(tmp_path, "LICENSE")
    first_archive = build_tool.build_zip(tmp_path)
    first_archive.write_text("not a zip", encoding="utf-8")

    rebuilt_archive = build_tool.build_zip(tmp_path)

    assert rebuilt_archive == first_archive
    assert zipfile.is_zipfile(rebuilt_archive)
    assert _archive_names(rebuilt_archive) == {"LICENSE"}


def test_build_cli_selects_requested_artifact(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[str, Path]] = []

    monkeypatch.setattr(build_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        build_tool,
        "build_zip",
        lambda root: calls.append(("zip", root)) or root / "dist" / "archive.zip",
    )
    monkeypatch.setattr(
        build_tool,
        "build_skill",
        lambda root: calls.append(("skill", root)) or root / "dist" / "archive.skill",
    )

    assert build_tool.main([]) == 0
    assert build_tool.main(["--skill"]) == 0
    assert calls == [("zip", tmp_path), ("skill", tmp_path)]
