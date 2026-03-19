"""Contract checks for GitHub-flavored Markdown in `skills/` and `templates/`."""

from __future__ import annotations

from pathlib import Path

from modules.markdown_contract import check_markdown_file, check_repo


def test_markdown_contract_has_no_issues() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    issues = check_repo(repo_root)
    if issues:
        rendered = "\n".join(
            f"{issue.path.relative_to(repo_root)}:{issue.line}: {issue.message}"
            for issue in issues
        )
        raise AssertionError(f"Markdown contract issues found:\n{rendered}")


def test_markdown_contract_allows_canonical_ordered_lists(tmp_path: Path) -> None:
    path = tmp_path / "canonical.md"
    path.write_text("1. one\n1. two\n1. three\n", encoding="utf-8")

    issues = check_markdown_file(path, tmp_path)

    assert not [issue for issue in issues if "Ordered list numbering" in issue.message]


def test_markdown_contract_allows_sequential_ordered_lists(tmp_path: Path) -> None:
    path = tmp_path / "sequential.md"
    path.write_text("1. one\n2. two\n3. three\n", encoding="utf-8")

    issues = check_markdown_file(path, tmp_path)

    assert not [issue for issue in issues if "Ordered list numbering" in issue.message]


def test_markdown_contract_rejects_mixed_ordered_lists(tmp_path: Path) -> None:
    path = tmp_path / "mixed.md"
    path.write_text("1. one\n1. two\n3. three\n", encoding="utf-8")

    issues = check_markdown_file(path, tmp_path)

    assert [issue for issue in issues if "Ordered list numbering" in issue.message]
