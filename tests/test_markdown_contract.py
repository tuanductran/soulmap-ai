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


def test_markdown_contract_does_not_flag_numeric_comments_in_code_fences(
    tmp_path: Path,
) -> None:
    """Regression: bash comments like '# 1. do X' inside fences must not be
    flagged as headings with numeric prefixes."""
    path = tmp_path / "code-fence.md"
    path.write_text(
        "# Valid heading\n\n"
        "```bash\n"
        "# 1. Always start from main\n"
        "git checkout main\n"
        "# 2. Create a branch\n"
        "git checkout -b fix/thing\n"
        "# 3. Push it\n"
        "git push origin fix/thing\n"
        "```\n",
        encoding="utf-8",
    )
    issues = check_markdown_file(path, tmp_path)
    numeric_issues = [i for i in issues if "numeric prefix" in i.message]
    assert not numeric_issues, (
        f"False positive: numeric comments in code fences should not be flagged. "
        f"Got: {numeric_issues}"
    )


def test_markdown_contract_does_not_flag_bad_atx_in_code_fences(
    tmp_path: Path,
) -> None:
    """Regression: ##nospace inside a fence must not be flagged as bad ATX heading."""
    path = tmp_path / "code-fence.md"
    path.write_text(
        "# Valid heading\n\n```bash\n##not-a-heading\n```\n",
        encoding="utf-8",
    )
    issues = check_markdown_file(path, tmp_path)
    atx_issues = [i for i in issues if "ATX heading missing" in i.message]
    assert not atx_issues, (
        f"False positive: bad ATX inside code fence should not be flagged. Got: {atx_issues}"
    )


def test_markdown_contract_does_not_flag_image_alt_in_code_fences(
    tmp_path: Path,
) -> None:
    """Regression: image with no alt text inside a fence must not be flagged."""
    path = tmp_path / "code-fence.md"
    path.write_text(
        "# Valid heading\n\n```html\n![](image.png)\n```\n",
        encoding="utf-8",
    )
    issues = check_markdown_file(path, tmp_path)
    alt_issues = [i for i in issues if "alt text" in i.message]
    assert not alt_issues, (
        f"False positive: image without alt text inside fence should not be flagged. Got: {alt_issues}"
    )


def test_markdown_contract_does_not_flag_links_in_code_fences(
    tmp_path: Path,
) -> None:
    """Regression: relative links inside a fence must not be checked for existence."""
    path = tmp_path / "code-fence.md"
    path.write_text(
        "# Valid heading\n\n```bash\n[example](nonexistent_file.py)\n```\n",
        encoding="utf-8",
    )
    issues = check_markdown_file(path, tmp_path)
    link_issues = [
        i for i in issues if "Broken" in i.message or "link" in i.message.lower()
    ]
    assert not link_issues, (
        f"False positive: relative link inside code fence should not be checked. Got: {link_issues}"
    )
