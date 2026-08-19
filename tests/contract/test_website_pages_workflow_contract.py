from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "website-pages.yml"
WEBSITE_DOC = REPO_ROOT / "docs" / "product" / "WEBSITE.md"


def test_pages_workflow_builds_and_verifies_static_site() -> None:
    content = WORKFLOW.read_text(encoding="utf-8")

    for marker in (
        "src/soulmap/web/**",
        "uv run soulmap web",
        "--export-static",
        "--base-path",
        "scripts/verify_static_site.py",
        "actions/upload-artifact@v7",
    ):
        assert marker in content

    assert "dist/soulmap-ai" not in content
    assert "skills/" not in content


def test_pages_workflow_publishes_only_main_to_gh_pages() -> None:
    content = WORKFLOW.read_text(encoding="utf-8")

    assert "github.event_name == 'push'" in content
    assert "github.ref == 'refs/heads/main'" in content
    assert "needs: build" in content
    assert "contents: write" in content
    assert "git push --force origin gh-pages" in content
    assert "touch .nojekyll" in content


def test_website_docs_describe_static_export_and_branch_boundary() -> None:
    content = WEBSITE_DOC.read_text(encoding="utf-8")

    for marker in (
        "--export-static",
        "--base-path",
        "gh-pages",
        "static output",
        "never a source of SoulMap doctrine",
    ):
        assert marker in content
