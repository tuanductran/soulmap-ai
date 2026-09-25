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
    assert "gh pr create" in workflow
    assert "release/prep-" in workflow
    assert "release-finalize" in workflow
    assert "git push --follow-tags" not in workflow
    assert "softprops/action-gh-release" not in workflow


def test_release_finalize_publishes_only_after_merged_main_verification() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-finalize.yml").read_text()

    assert "types: [closed]" in workflow
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
    assert "Generate release artifact attestations" in workflow
    assert (
        "actions/attest@508db95dd578ae2727ebd6217d5ba78e4fbda05d # v4.2.1"
        in workflow
    )
    assert "dist/soulmap-ai.zip" in workflow
    assert "dist/soulmap-ai.skill" in workflow
    assert "dist/soulmap-ai-library.json" in workflow
    assert "Create immutable release tag" in workflow
    assert 'existing_commit="$(git rev-parse "$TAG^{commit}")"' in workflow
    assert "reusing it without moving it" in workflow
    assert "git tag -a" in workflow
    assert 'git push origin "$TAG"' in workflow
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
