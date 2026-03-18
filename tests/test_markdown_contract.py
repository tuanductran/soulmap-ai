"""Contract checks for GitHub-flavored Markdown in `skills/` and `templates/`."""

from __future__ import annotations

from pathlib import Path

from modules.markdown_contract import check_repo


def test_markdown_contract_has_no_issues() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    issues = check_repo(repo_root)
    if issues:
        rendered = "\n".join(
            f"{issue.path.relative_to(repo_root)}:{issue.line}: {issue.message}"
            for issue in issues
        )
        raise AssertionError(f"Markdown contract issues found:\n{rendered}")
