"""Contract tests for release operational workflows."""

from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_release_prep_creates_a_protected_release_pr() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text()

    assert "name: Release Prep" in workflow
    assert "workflow_dispatch" in workflow
    assert "if: github.ref == 'refs/heads/main'" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: write" in workflow
    assert "SOULMAP_RELEASE_TOKEN" in workflow
    assert "persist-credentials: true" in workflow
    assert "git push --set-upstream origin" in workflow
    assert "python .github/python/release/create_pr.py" in workflow
    assert "SOULMAP_RELEASE_TOKEN: ${{ secrets.SOULMAP_RELEASE_TOKEN }}" in workflow
    assert "RELEASE_BRANCH: ${{ steps.bump.outputs.branch }}" in workflow
    assert "RELEASE_TAG: ${{ steps.bump.outputs.tag }}" in workflow
    assert "gh pr create" not in workflow
    assert "release/prep-" in workflow
    assert "release-finalize" in workflow
    assert "git push --follow-tags" not in workflow
    assert "softprops/action-gh-release" not in workflow


def test_release_finalize_publishes_only_after_merged_main_verification() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-finalize.yml").read_text()

    assert "types: [closed]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "merge_commit_sha:" in workflow
    assert "inputs.merge_commit_sha" in workflow
    assert 'branches: ["main"]' in workflow
    assert "github.event.pull_request.merged == true" in workflow
    assert "startsWith(github.event.pull_request.head.ref, 'release/prep-')" in workflow
    assert "github.event.pull_request.merge_commit_sha" in workflow
    assert "Verify checkout is the merged release commit" in workflow
    assert "soulmap release-verify" in workflow
    assert "soulmap release-provenance" in workflow
    assert "soulmap release-health" in workflow
    assert "dist/release-provenance.json" in workflow
    assert "contents: write" in workflow
    assert "id-token: write" in workflow
    assert "attestations: write" in workflow
    assert workflow.count("name: Generate release artifact attestations") == 1
    assert (
        "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6 # v4.2.2" in workflow
    )
    assert "dist/soulmap-ai.zip" in workflow
    assert "dist/soulmap-ai.skill" in workflow
    assert "dist/soulmap-ai-library.json" in workflow
    assert "Create immutable release tag" in workflow
    assert "reusing it without moving it" in workflow
    assert "Checkout release tooling" in workflow
    assert "python .release-tools/.github/python/release_tag.py" in workflow
    assert "GITHUB_TOKEN: ${{ github.token }}" in workflow
    assert "git push origin" not in workflow
    assert "SOULMAP_RELEASE_TOKEN" not in workflow
    assert "Create GitHub Release" in workflow
    assert workflow.index(
        "Verify checkout is the merged release commit"
    ) < workflow.index("Verify merged release tree")
    assert workflow.index("Verify merged release tree") < workflow.index(
        "Create immutable release tag"
    )
    assert workflow.index("Verify downloaded release artifacts") < workflow.index(
        "Generate release artifact attestations"
    )
    assert workflow.index("Generate release artifact attestations") < workflow.index(
        "Create immutable release tag"
    )
    assert workflow.index("Verify downloaded release artifacts") < workflow.index(
        "Generate release artifact attestations"
    )
    assert workflow.index("Generate release artifact attestations") < workflow.index(
        "Create immutable release tag"
    )
    assert workflow.index("Create immutable release tag") < workflow.index(
        "Create GitHub Release"
    )


def test_rollback_workflow_is_read_only_and_checks_known_good_tag() -> None:
    workflow = (ROOT / ".github" / "workflows" / "rollback-verify.yml").read_text()

    assert "release_ref:" in workflow
    assert "contents: read" in workflow
    assert "release-verify" in workflow
    assert 'test "v${version}" = "${{ inputs.release_ref }}"' in workflow
    assert "rollback_ready" in workflow
    assert "contents: write" not in workflow


def test_release_health_preserves_verification_summary_for_publication() -> None:
    release_verify = (
        ROOT / "src" / "soulmap" / "devtools" / "packaging" / "release_verify.py"
    ).read_text()
    cleanup_block = """    for filename in (
        "soulmap-ai.zip",
        "soulmap-ai.skill",
        "soulmap-ai-library.json",
    ):
"""
    assert cleanup_block in release_verify
    assert '"release-verification.json"' not in cleanup_block


def test_release_tag_tool_uses_git_database_api_without_git_push() -> None:
    script = (ROOT / ".github" / "python" / "release_tag.py").read_text()

    assert "POST" in script
    assert "/git/tags" in script
    assert "/git/refs" in script
    assert '"Contents: write"' not in script
    assert "git push" not in script
    assert "refs/tags/" in script
    assert "reusing it without moving it" in script

def test_release_pr_tool_uses_pull_request_api_without_gh_cli() -> None:
    script = (ROOT / ".github" / "python" / "release" / "create_pr.py").read_text()

    assert '"/pulls"' in script
    assert '"SOULMAP_RELEASE_TOKEN"' in script
    assert '"RELEASE_BRANCH"' in script
    assert '"RELEASE_TAG"' in script
    assert "gh pr create" not in script
    assert "https://api.github.com" in script
\n