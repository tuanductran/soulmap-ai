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
        (4, "value = 1  # TODO inline comment should be inventoried too"),
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
