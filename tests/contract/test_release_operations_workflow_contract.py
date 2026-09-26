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
    assert "uses: $/src/action" in workflow
    assert "token: ${{ secrets.SOULMAP_RELEASE_TOKEN }}" in workflow
    assert "branch: ${{ steps.bump.outputs.branch }}" in workflow
    assert "tag: ${{ steps.bump.outputs.tag }}" in workflow
    assert "gh pr create" not in workflow
    assert "release/prep-" in workflow
    assert "git push --follow-tags" not in workflow
    assert "softprops/action-gh-release" not in workflow
    assert "operation: pull-request" in workflow


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
    assert "Configure git author" in workflow
    assert 'git config user.name "github-actions[bot]"' in workflow
    assert 'git config user.email "github-actions[bot]@users.noreply.github.com"' in workflow
    assert 'git push origin "$TAG"' in workflow
    assert "uses: $/src/action" in workflow
    assert "operation: release" in workflow
    assert "tag: v${{ needs.verify.outputs.version }}" in workflow
    assert "GITHUB_TOKEN: ${{ github.token }}" not in workflow
    assert "SOULMAP_RELEASE_TOKEN: ${{ secrets.SOULMAP_RELEASE_TOKEN }}" not in workflow
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
        "Publish GitHub Release"
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
    )
"""
    assert '"soulmap-ai.zip"' in release_verify
    assert '"soulmap-ai.skill"' in release_verify
    assert '"soulmap-ai-library.json"' in release_verify
    assert '"release-verification.json"' not in cleanup_block


def test_local_python_action_contains_github_operations() -> None:
    action = (ROOT / "src" / "action" / "__main__.py").read_text()
    assert "/pulls" in action
    assert "/releases" in action
    assert "GITHUB_OUTPUT" in action
    assert "API_VERSION = " in action
    assert "gh pr create" not in action
