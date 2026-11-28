from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from soulmap import cli as cli_tool
from soulmap.devtools.checks.skills_boundary import audit_markdown, audit_text
from soulmap.devtools.packaging import build_skill as build_tool
from soulmap.devtools.packaging import dev as dev_tool
from soulmap.devtools.packaging.members import is_safe_member_path


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
        "# internal files\n\nskills/private.md\n*.tmp\n.claude-plugin/README.md\n",
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
    _write(root, "skills/AGENTS.md", "repository instructions must not ship\n")
    _write(root, "skills/nested/CLAUDE.md", "agent entrypoint must not ship\n")
    _write(root, "skills/AGENTS.override.md", "agent entrypoint variant\n")
    _write(root, "skills/CLAUDE.local.md", "agent entrypoint variant\n")
    _write(root, "skills/.cursorrules", "agent entrypoint must not ship\n")
    _write(
        root, "skills/nested/.github/copilot-instructions.md", "local instructions\n"
    )
    _write(root, "AGENTS.md", "repository instructions must not ship\n")
    _write(root, "CLAUDE.md", "agent entrypoint must not ship\n")
    _write(root, "GEMINI.md", "agent entrypoint must not ship\n")
    _write(root, "CODEX.md", "agent entrypoint must not ship\n")
    _write(root, ".claude/CLAUDE.md", "local instructions\n")
    _write(root, ".github/agents/reviewer.md", "local instructions\n")
    _write(root, "skills/nested/.vscode/settings.json", "{}\n")
    _write(root, "src/soulmap/runtime/source_registry.py", "REGISTRY = {}\n")
    _write(root, "templates/internal.md")
    _write(root, ".claude-plugin/marketplace.json", "{}\n")
    _write(root, ".claude-plugin/metadata.md", "Package metadata only.\n")
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
        ".claude-plugin/metadata.md",
    }
    assert ".claude-plugin/README.md" not in skill_names


def test_build_archives_exclude_agent_entrypoints_and_local_config(
    tmp_path: Path,
) -> None:
    _create_source_tree(tmp_path)

    zip_path = build_tool.build_zip(tmp_path)
    skill_path = build_tool.build_skill(tmp_path)

    excluded_names = {
        "agents.md",
        "claude.md",
        "agents.override.md",
        "claude.local.md",
        "gemini.md",
        "codex.md",
        "copilot-instructions.md",
        ".cursorrules",
    }
    excluded_directories = {".claude", ".cursor", ".github", ".vscode", ".idea", ".git"}
    for archive_path in (zip_path, skill_path):
        names = _archive_names(archive_path)
        assert not any(
            name.rsplit("/", 1)[-1].casefold() in excluded_names for name in names
        )
        assert not any(
            any(
                part.casefold() in excluded_directories for part in name.split("/")[:-1]
            )
            for name in names
        )

    # The .skill artifact retains only its required plugin metadata.
    assert ".claude-plugin/marketplace.json" in _archive_names(skill_path)
    assert ".claude-plugin/marketplace.json" not in _archive_names(zip_path)


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

    assert dev_tool.main(["--once", "--no-audit"]) == 0

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
    assert (skill_tree / ".claude-plugin/metadata.md").is_file()
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
    assert cli_tool.main(["dev", "--once"]) == 0
    assert calls == [("build", []), ("dev", ["--once"])]


def test_build_refuses_artifacts_with_language_leakage_in_root_entrypoint(
    tmp_path: Path,
) -> None:
    _create_source_tree(tmp_path)
    _write(tmp_path, "SKILL.md", "# SoulMap\n\nPython must not ship.\n")

    with pytest.raises(ValueError, match="Shipped content boundary failed"):
        build_tool.build_zip(tmp_path)

    with pytest.raises(ValueError, match="Shipped content boundary failed"):
        build_tool.build_skill(tmp_path)


def test_build_refuses_language_leakage_in_plugin_metadata(
    tmp_path: Path,
) -> None:
    _create_source_tree(tmp_path)
    _write(
        tmp_path,
        ".claude-plugin/marketplace.json",
        '{"description": "Python tooling is not user-facing SoulMap knowledge."}\n',
    )

    with pytest.raises(ValueError, match="Shipped content boundary failed"):
        build_tool.build_zip(tmp_path)

    with pytest.raises(ValueError, match="Shipped content boundary failed"):
        build_tool.build_skill(tmp_path)


def test_built_archives_contain_only_language_neutral_text(
    tmp_path: Path,
) -> None:
    _create_source_tree(tmp_path)
    archives = build_tool.build_all(tmp_path)

    for archive_path in archives:
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                content = archive.read(member).decode("utf-8", errors="ignore")
                if member.casefold().endswith(".md"):
                    assert audit_markdown(member, content) == []
                else:
                    assert audit_text(member, content) == []


def test_build_rejects_symlinked_skill_file(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    _write(tmp_path, "outside.md", "private local content\n")
    skills = tmp_path / "skills"
    skills.mkdir()
    try:
        (skills / "linked.md").symlink_to(outside)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"symlink creation is unavailable: {error}")

    with pytest.raises(ValueError, match="Symlinked package source"):
        build_tool._iter_inputs(tmp_path)


def test_build_rejects_symlinked_skills_root(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    _write(outside, "linked.md", "private local content\n")
    try:
        (tmp_path / "skills").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"directory symlink creation is unavailable: {error}")

    with pytest.raises(ValueError, match="Symlinked package source root"):
        build_tool._iter_inputs(tmp_path)


def test_build_rejects_symlinked_core_manifest(tmp_path: Path) -> None:
    target = _write(tmp_path, "outside-skill.md", "# Private local content\n")
    try:
        (tmp_path / "SKILL.md").symlink_to(target)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"symlink creation is unavailable: {error}")

    with pytest.raises(ValueError, match="Symlinked package source"):
        build_tool._iter_inputs(tmp_path)


@pytest.mark.parametrize(
    "member_name",
    [
        "C:/outside.txt",
        "C:outside.txt",
        "skills/..\\outside.txt",
        "skills/bad\\name.md",
    ],
)
def test_archive_member_path_safety_is_cross_platform(member_name: str) -> None:
    assert is_safe_member_path(member_name) is False


@pytest.mark.parametrize(
    "member_name",
    [
        "skills/.. /file.md",
        "skills/.. . /file.md",
        "skills/parent . /file.md",
        "skills/parent. /file.md",
        "skills/name. /file.md",
    ],
)
def test_archive_member_rejects_windows_trimmed_component_variants(
    member_name: str,
) -> None:
    assert is_safe_member_path(member_name) is False


@pytest.mark.skipif(os.name == "nt", reason="POSIX permits backslashes in filenames")
def test_build_skips_ignored_backslash_source_before_path_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path, "LICENSE")
    _write(tmp_path, "SOULMAP.md")
    _write(tmp_path, "SKILL.md")
    _write(tmp_path, "skills/ignored\\name.md")
    (tmp_path / ".distignore").write_text("skills/ignored\\name.md\n", encoding="utf-8")
    monkeypatch.setattr(build_tool, "audit_shipped_content", lambda _root: [])

    archive_path = build_tool.build_zip(tmp_path)

    with zipfile.ZipFile(archive_path) as archive:
        assert "skills/ignored\\name.md" not in archive.namelist()



def test_watch_filter_includes_sources_and_excludes_generated_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dev_tool, "REPO_ROOT", tmp_path)
    from watchfiles import Change

    assert dev_tool._watch_filter(Change.modified, str(tmp_path / "skills/new.md"))
    assert dev_tool._watch_filter(Change.added, str(tmp_path / "docs/guide.md"))
    assert dev_tool._watch_filter(Change.modified, str(tmp_path / "src/soulmap/cli.py"))
    assert not dev_tool._watch_filter(Change.modified, str(tmp_path / "dist/generated.md"))
    assert not dev_tool._watch_filter(Change.modified, str(tmp_path / ".soulmap/zip/old.md"))
    assert not dev_tool._watch_filter(Change.modified, str(tmp_path / ".venv/site-packages/pkg.py"))


def test_dev_runs_python_and_resource_audits_when_enabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dev_tool, "REPO_ROOT", tmp_path)
    calls: list[tuple[str, list[str]]] = []

    import scripts.audit_python_reachability as python_audit
    import scripts.audit_resource_inventory as resource_audit

    monkeypatch.setattr(
        python_audit, "main",
        lambda args: calls.append(("python", args)) or 0,
    )
    monkeypatch.setattr(
        resource_audit, "main",
        lambda args: calls.append(("resources", args)) or 0,
    )

    assert dev_tool._run_audits(tmp_path) == 0
    assert calls == [
        ("python", ["--root", str(tmp_path)]),
        ("resources", ["--root", str(tmp_path)]),
    ]
