from __future__ import annotations

from pathlib import Path

from scripts.audit_repo_consistency import comment_candidates, path_reference_hits


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


def test_directory_reference_hits_finds_path_forms_without_matching_similar_names() -> None:
    from scripts.audit_repo_consistency import directory_reference_hits

    content = (
        "See retired-assets/manifest.json.\\n"
        "Old path: ./retired-assets\\\\manifest.json\\n"
        "Not the same: retired-assets-old/manifest.json.\\n"
        "Not root-relative: docs/retired-assets/manifest.json.\\n"
        "The retired-assets directory was discussed in prose.\\n"
    )

    assert directory_reference_hits(content, "retired-assets") == [
        (1, "directory-path", "See retired-assets/manifest.json."),
        (2, "directory-path", "Old path: ./retired-assets\\\\manifest.json"),
    ]


def test_directory_reference_hits_finds_quoted_root_directory_tokens() -> None:
    from scripts.audit_repo_consistency import directory_reference_hits

    content = 'Path("retired-assets") is a path configuration.\\n'
    assert directory_reference_hits(content, "retired-assets") == [
        (1, "quoted-directory-token", 'Path("retired-assets") is a path configuration.')
    ]


def test_deleted_directories_only_includes_absent_ancestors(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import audit_repo_consistency as audit

    monkeypatch.setattr(
        audit, "tracked_files", lambda root: [root / "src" / "live.py"]
    )

    assert audit.deleted_directories(
        tmp_path, ["retired-assets/manifest.json", "src/removed.py"]
    ) == ["retired-assets"]
