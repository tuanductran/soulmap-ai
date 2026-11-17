"""Contract tests for release operational workflows."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_release_prep_creates_a_protected_release_pr() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text()

    assert "name: Release Prep" in workflow
    assert "workflow_dispatch" in workflow
    assert "if: github.ref == 'refs/heads/main'" in workflow
    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "token: ${{ secrets.SOULMAP_RELEASE_TOKEN }}" in workflow
    assert "pull-requests: write" not in workflow
    assert "SOULMAP_RELEASE_TOKEN" in workflow
    assert "persist-credentials: false" in workflow
    assert "operation: branch" in workflow
    assert "target-sha: ${{ steps.bump.outputs.sha }}" in workflow
    assert (
        'git -c "http.extraheader=AUTHORIZATION: basic $auth_header" push'
        not in workflow
    )
    assert "uses: ./src/action" in workflow
    assert "branch: ${{ steps.bump.outputs.branch }}" in workflow
    assert "tag: ${{ steps.bump.outputs.tag }}" in workflow
    assert "gh pr create" not in workflow
    assert "release/prep-" in workflow
    assert "git push --follow-tags" not in workflow
    assert "softprops/action-gh-release" not in workflow
    assert "operation: pull-request" in workflow
    assert "base64" not in workflow


def test_release_finalize_publishes_only_after_merged_main_verification() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-finalize.yml").read_text()

    assert "types: [closed]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "merge_commit_sha:" in workflow
    assert "inputs.merge_commit_sha" in workflow
    assert 'branches: ["main"]' in workflow
    assert "github.event.pull_request.merged == true" in workflow
    assert (
        "github.event.pull_request.head.repo.full_name == github.repository" in workflow
    )
    assert (
        "github.event.pull_request.base.repo.full_name == github.repository" in workflow
    )
    assert "startsWith(github.event.pull_request.head.ref, 'release/prep-')" in workflow
    assert workflow.count('git merge-base --is-ancestor "$MERGE_SHA" origin/main') == 2
    assert "github.event.pull_request.merge_commit_sha" in workflow
    assert "Verify checkout is the merged release commit" in workflow
    assert "soulmap release-gate" in workflow
    assert "soulmap release-verify" not in workflow
    assert "soulmap release-provenance" not in workflow
    assert "soulmap release-health" not in workflow
    assert "dist/release-provenance.json" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "id-token: write" in workflow
    assert (
        "SOULMAP_RELEASE_TOKEN must be configured for GitHub Release publication."
        in workflow
    )
    assert 'if [ -z "${RELEASE_TOKEN//[[:space:]]/}" ]; then' in workflow
    assert "token: ${{ secrets.SOULMAP_RELEASE_TOKEN }}" in workflow
    assert "token: ${{ github.token }}" not in workflow
    assert "persist-credentials: false" in workflow
    assert "operation: tag" in workflow
    assert "attestations: write" in workflow
    assert workflow.count("name: Generate release artifact attestations") == 1
    assert (
        "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6 # v4.2.2" in workflow
    )
    assert "dist/soulmap-ai.zip" in workflow
    assert "dist/soulmap-ai.skill" in workflow
    assert "dist/soulmap-ai-library.json" in workflow
    assert "Create immutable release tag through Python action" in workflow
    assert "target-sha:" in workflow
    assert "uses: ./src/action" in workflow
    assert "tag: v${{ needs.verify.outputs.version }}" in workflow
    assert 'generate-release-notes: "true"' in workflow
    assert "GITHUB_TOKEN: ${{ github.token }}" not in workflow
    assert workflow.index(
        "Verify checkout is the merged release commit"
    ) < workflow.index("Verify merged release tree")
    assert workflow.index("Verify merged release tree") < workflow.index(
        "Create immutable release tag"
    )
    assert workflow.index("Verify downloaded release artifacts") < workflow.index(
        "Generate release artifact attestations"
    )
    assert workflow.index("Verify release token is configured") < workflow.index(
        "Generate release artifact attestations"
    )
    assert workflow.index("Generate release artifact attestations") < workflow.index(
        "Create immutable release tag"
    )
    assert workflow.index("Verify release token is configured") < workflow.index(
        "Create immutable release tag through Python action"
    )
    assert workflow.index(
        "Create immutable release tag through Python action"
    ) < workflow.index("Publish GitHub Release")

    # Manual recovery must prove that the supplied SHA is the merge commit of
    # a merged release/prep-* PR targeting this repository's main branch.
    assert (
        "Verify manually supplied SHA belongs to a merged release preparation PR"
        in workflow
    )
    assert "if: github.event_name == 'workflow_dispatch'" in workflow
    assert "commits/${MERGE_SHA}/pulls?per_page=100" in workflow
    assert "python3 scripts/verify_release_finalize_provenance.py" in workflow
    assert "associated-pull-requests.json" in workflow
    assert workflow.index(
        "Verify manually supplied SHA belongs to a merged release preparation PR"
    ) < workflow.index("Install uv")


def test_manual_release_provenance_guard_checks_observable_outcomes() -> None:
    script = ROOT / "scripts" / "verify_release_finalize_provenance.py"
    merge_sha = "a" * 40
    valid_pull_request = {
        "merged_at": "2026-11-17T00:00:00Z",
        "merge_commit_sha": merge_sha,
        "base": {
            "ref": "main",
            "repo": {"full_name": "tuanductran/soulmap-ai"},
        },
        "head": {
            "ref": "release/prep-1.2.3",
            "repo": {"full_name": "tuanductran/soulmap-ai"},
        },
    }
    invalid_pull_requests = [
        {**valid_pull_request, "merge_commit_sha": "b" * 40},
        {**valid_pull_request, "merged_at": None},
        {
            **valid_pull_request,
            "base": {**valid_pull_request["base"], "ref": "develop"},
        },
        {
            **valid_pull_request,
            "head": {**valid_pull_request["head"], "ref": "feature/not-a-release"},
        },
        {
            **valid_pull_request,
            "head": {
                **valid_pull_request["head"],
                "repo": {"full_name": "fork/soulmap-ai"},
            },
        },
    ]

    with tempfile.TemporaryDirectory() as directory:
        response_path = Path(directory) / "associated-pull-requests.json"

        def run_guard(
            pull_requests: list[dict[str, object]],
        ) -> subprocess.CompletedProcess[str]:
            response_path.write_text(json.dumps(pull_requests), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(script), str(response_path), merge_sha],
                check=False,
                capture_output=True,
                text=True,
            )

        valid_result = run_guard([valid_pull_request])
        assert valid_result.returncode == 0, valid_result.stderr

        for invalid_pull_request in invalid_pull_requests:
            invalid_result = run_guard([invalid_pull_request])
            assert invalid_result.returncode == 1


def test_rollback_workflow_is_read_only_and_checks_known_good_tag() -> None:
    workflow = (ROOT / ".github" / "workflows" / "rollback-verify.yml").read_text()
    summary_script = (ROOT / "scripts" / "emit_rollback_summary.py").read_text()

    assert "release_ref:" in workflow
    assert "contents: read" in workflow
    assert "release-verify" in workflow
    assert "RELEASE_REF: ${{ inputs.release_ref }}" in workflow
    assert 'test "v${version}" = "$RELEASE_REF"' in workflow
    assert 'scripts/emit_rollback_summary.py --release-ref "$RELEASE_REF"' in workflow
    assert 'test "v${version}" = "${{ inputs.release_ref }}"' not in workflow
    assert "rollback_ready" in summary_script
    assert "python - <<'PY'" not in workflow
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
    action_dir = ROOT / "src" / "action"
    action = (action_dir / "__main__.py").read_text()
    operations = (action_dir / "operations.py").read_text()
    refs = (action_dir / "refs.py").read_text()
    releases = (action_dir / "releases.py").read_text()
    inputs = (action_dir / "inputs.py").read_text()
    constants = (action_dir / "constants.py").read_text()
    combined = "\\n".join((action, operations, refs, releases, inputs, constants))
    assert "/pulls" in operations
    assert "/git/refs" in refs
    assert "def create_branch(" in refs
    assert '["git", "push", "origin", f"HEAD:refs/heads/{branch}"]' in refs
    assert "GIT_CONFIG_VALUE_0" in refs
    assert 'operation == "branch"' in action
    assert "/releases" in releases
    assert "GITHUB_OUTPUT" in inputs
    assert "API_VERSION = " in constants
    assert "gh pr create" not in combined
