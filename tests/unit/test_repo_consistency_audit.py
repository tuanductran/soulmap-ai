from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_repo_consistency import (
    comment_candidates,
    deleted_directories,
    deleted_paths,
    directory_reference_hits,
    path_reference_hits,
)


def test_comment_candidates_only_reports_review_markers() -> None:
    content = (
        "# TODO: remove after migration\n"
        "# This invariant protects the parser boundary.\n"
        "# return old_value\n"
        "value = 1  # TODO inline comment should be inventoried too\n"
    )

    assert comment_candidates(Path("module.py"), content) == [
        (1, "# TODO: remove after migration"),
        (3, "# return old_value"),
        (4, "# TODO inline comment should be inventoried too"),
    ]


def test_comment_candidates_detects_html_comment_markers() -> None:
    content = (
        "<!-- TODO: remove the obsolete note -->\n"
        "<!-- current context remains useful -->\n"
    )

    assert comment_candidates(Path("README.md"), content) == [
        (1, "<!-- TODO: remove the obsolete note -->")
    ]


def test_path_reference_hits_distinguishes_exact_and_basename() -> None:
    content = (
        "See docs/old-guide.md for details.\n"
        "The old-guide.md reference may also be stale.\n"
    )

    assert path_reference_hits(content, "docs/old-guide.md") == [
        (1, "exact-path", "See docs/old-guide.md for details."),
        (2, "basename-only", "The old-guide.md reference may also be stale."),
    ]


def test_path_reference_hits_ignores_current_file_with_same_basename() -> None:
    content = (
        "[Repository contract](repo-contract.md)\\n"
        "See docs/engineering/repo-contract.md for details.\\n"
    )

    assert path_reference_hits(
        content,
        "docs/repo-contract.md",
        source_path=Path("docs/engineering/DEV.md"),
        current_paths={"docs/engineering/repo-contract.md"},
    ) == []


def test_path_reference_hits_keeps_unresolved_basename_candidate() -> None:
    assert path_reference_hits(
        "The old repo-contract.md reference needs review.\n",
        "docs/repo-contract.md",
        source_path=Path("README.md"),
        current_paths={"docs/engineering/repo-contract.md"},
    ) == [(1, "basename-only", "The old repo-contract.md reference needs review.")]


def test_path_reference_hits_ignores_generic_skill_basename() -> None:
    content = "Current skill documents use SKILL.md as their conventional filename.\n"

    assert path_reference_hits(content, "skills/frameworks/SKILL.md") == []


def test_deleted_paths_excludes_paths_reused_as_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "scripts.audit_repo_consistency.run_git",
        lambda root, *args: ".claude/hooks\nsrc/removed.py\n",
    )
    monkeypatch.setattr(
        "scripts.audit_repo_consistency.tracked_files",
        lambda root: [
            root / ".claude" / "hooks" / "session-start.sh",
            root / "src" / "live.py",
        ],
    )

    assert deleted_paths(tmp_path, base="origin/main", history=False) == [
        "src/removed.py"
    ]


def test_directory_reference_paths_avoid_similar_names() -> None:
    content = "\n".join(
        [
            "See retired-assets/manifest.json.",
            r"Old path: ./retired-assets\manifest.json",
            "Not the same: retired-assets-old/manifest.json.",
            "Not root-relative: docs/retired-assets/manifest.json.",
            "The retired-assets directory was discussed in prose.",
        ]
    )

    assert directory_reference_hits(content, "retired-assets") == [
        (1, "directory-path", "See retired-assets/manifest.json."),
        (2, "directory-path", r"Old path: ./retired-assets\manifest.json"),
    ]


def test_directory_reference_hits_finds_quoted_root_directory_tokens() -> None:
    content = 'Path("retired-assets") is a path configuration.'

    assert directory_reference_hits(content, "retired-assets") == [
        (
            1,
            "quoted-directory-token",
            'Path("retired-assets") is a path configuration.',
        )
    ]


def test_deleted_directories_only_includes_absent_ancestors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "scripts.audit_repo_consistency.tracked_files",
        lambda root: [root / "src" / "live.py"],
    )

    assert deleted_directories(
        tmp_path, ["retired-assets/manifest.json", "src/removed.py"]
    ) == ["retired-assets"]


def test_path_reference_hits_avoid_substring_matches() -> None:
    content = "\n".join(
        [
            "Exact path: docs/old-guide.md.",
            "Not the same path: docs/old-guide.md.bak",
            "Not the same basename: old-guide.mdx",
            r"Windows path: docs\old-guide.md",
        ]
    )

    assert path_reference_hits(content, "docs/old-guide.md") == [
        (1, "exact-path", "Exact path: docs/old-guide.md."),
        (4, "backslash-path", r"Windows path: docs\old-guide.md"),
    ]


def test_main_returns_incomplete_status_for_unreadable_tracked_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    unreadable = tmp_path / "unreadable.md"
    unreadable.write_bytes(b"\xff\xfe\xfa")
    monkeypatch.setattr(
        "scripts.audit_repo_consistency.tracked_files", lambda root: [unreadable]
    )

    from scripts.audit_repo_consistency import main

    exit_code = main(["--root", str(tmp_path), "--comments-only"])
    output = capsys.readouterr().out

    assert exit_code == 2
    assert "AUDIT LIMITATION:" in output
    assert "UnicodeDecodeError" in output
    assert "INCOMPLETE:" in output
