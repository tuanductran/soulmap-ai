from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_repo_consistency import (
    comment_candidates,
    deleted_directories,
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
