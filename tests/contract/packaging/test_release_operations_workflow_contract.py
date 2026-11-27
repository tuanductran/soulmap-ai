"""Contract tests for release operational workflows."""

import json
import os
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
    assert "environment:" not in workflow
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
    assert "Create run-bound release provenance manifest" in workflow
    assert "scripts/create_release_prep_provenance.py" in workflow
    assert "Record durable release provenance on pull request" in workflow
    assert "GH_TOKEN: ${{ secrets.SOULMAP_RELEASE_TOKEN }}" in workflow
    assert "EXPECTED_TOKEN_ACTOR: tuanductran" in workflow
    assert "gh api user --jq .login" in workflow
    assert "soulmap-release-prep-provenance:v1" in workflow
    assert "issues/$pr_number/comments" in workflow
    assert workflow.index("gh api user --jq .login") < workflow.index(
        "issues/$pr_number/comments"
    )
    assert (
        "GITHUB_WORKFLOW_REF"
        in (ROOT / "scripts" / "create_release_prep_provenance.py").read_text()
    )
    assert (
        "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9" in workflow
    )
    assert "release-prep-provenance-${{ github.run_id }}" in workflow
    assert "retention-days: 90" in workflow


def test_release_finalize_publishes_only_after_merged_main_verification() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-finalize.yml").read_text()

    assert "types: [closed]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "merge_commit_sha:" in workflow
    assert "inputs.merge_commit_sha" in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert "Verify recovery dispatch ref exactly matches main" in workflow
    assert 'if [ "$GITHUB_REF" != "refs/heads/main" ]; then' in workflow
    assert workflow.index(
        "Verify recovery dispatch ref exactly matches main"
    ) < workflow.index("actions/checkout@")
    assert 'branches: ["main"]' in workflow
    assert "github.event.pull_request.merged == true" in workflow
    assert "startsWith(github.event.pull_request.head.ref, 'release/prep-')" in workflow
    assert workflow.count('git merge-base --is-ancestor "$MERGE_SHA" origin/main') == 2
    assert "github.event.pull_request.merge_commit_sha" in workflow
    assert "Verify checkout is the merged release commit" in workflow
    assert "soulmap release-gate" in workflow
    assert "dist/release-provenance.json" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: read" in workflow
    assert "actions: read" in workflow
    assert "id-token: write" in workflow
    assert "attestations: write" in workflow
    assert "environment:" not in workflow
    assert "SOULMAP_RELEASE_TOKEN must be configured as a repository secret." in workflow
    assert "secrets.SOULMAP_RELEASE_TOKEN" in workflow
    assert "token: ${{ github.token }}" not in workflow
    assert "persist-credentials: false" in workflow
    assert "operation: tag" in workflow
    assert workflow.count("name: Generate release artifact attestations") == 1
    assert (
        "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6 # v4.2.2" in workflow
    )
    assert "dist/soulmap-ai.zip" in workflow
    assert "dist/soulmap-ai.skill" in workflow
    assert "dist/soulmap-ai-library.json" in workflow
    assert "target-sha:" in workflow
    pinned_action = (
        "tuanductran/soulmap-ai/src/action@dbc92c971f3ef2639000c1481c23bb62eaec720f"
    )
    assert workflow.count(f"uses: {pinned_action}") == 2
    assert "uses: ./src/action" not in workflow
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

    # Both automatic and recovery paths fetch and validate the same PR metadata
    # and complete changed-file list before building release artifacts.
    assert "Verify release preparation PR provenance and changed paths" in workflow
    assert "commits/${MERGE_SHA}/pulls?per_page=100" in workflow
    assert "pulls/${pr_number}/files?per_page=100" in workflow
    assert "gh api --paginate --slurp" in workflow
    assert "TRUSTED_WORKFLOW_SHA: ${{ github.workflow_sha }}" in workflow
    assert (
        'git show "${TRUSTED_WORKFLOW_SHA}:scripts/verify_release_finalize_provenance.py"'
        in workflow
    )
    assert 'python3 "$trusted_verifier"' in workflow
    assert "python3 scripts/verify_release_finalize_provenance.py" not in workflow
    assert "The immutable run-scoped artifact is authoritative." in workflow
    assert 'gh run download "$run_id"' in workflow
    assert '--name "$artifact_name"' in workflow
    assert (
        'candidate_manifest="$candidate_dir/release-prep-provenance.json"' in workflow
    )
    assert 'selected_manifest="$candidate_manifest"' in workflow
    assert 'cp "$selected_manifest" "$manifest"' in workflow
    assert workflow.index('gh run download "$run_id"') < workflow.index(
        'python3 "$trusted_verifier"'
    )
    assert workflow.index('test -s "$candidate_manifest"') < workflow.index(
        'python3 "$trusted_verifier"'
    )
    assert (
        "Recovery intentionally fails closed after GitHub's 90-day retention."
        in workflow
    )
    assert "issues/${pr_number}/comments?per_page=100" in workflow
    assert "actions/runs/${run_id}/artifacts?per_page=100" in workflow
    assert "actions/runs/${run_id}/attempts/${attempt}" in workflow
    assert "selected_artifact_name" in workflow
    assert '"$selected_artifact_name"' in workflow
    assert "run_attempt is the latest attempt" in workflow
    assert '[ "$selected_count" -ne 1 ]' in workflow
    assert "pr_head_sha" in workflow
    assert "release_head_sha == $release_head_sha" in workflow
    assert ".head_sha == $manifest[0].run_head_sha" in workflow
    assert ".head_sha == $manifest[0].workflow_sha" not in workflow
    assert 'git merge-base --is-ancestor "$workflow_sha" "$run_head_sha"' in workflow
    assert 'git merge-base --is-ancestor "$run_head_sha" origin/main' in workflow
    assert "jq -er '.run_attempt'" not in workflow
    verifier = (ROOT / "scripts" / "verify_release_finalize_provenance.py").read_text()
    assert "_has_matching_owner_provenance_comment" in verifier
    assert "created_at != updated_at" not in verifier
    assert "release-pr-comments.json" in workflow
    assert "gh run download" in workflow
    assert "release-pr-files.json" in workflow
    assert workflow.index(
        "Verify release preparation PR provenance and changed paths"
    ) < workflow.index("Install uv")


def test_release_prep_provenance_manifest_binds_run_to_exact_commit() -> None:
    script = ROOT / "scripts" / "create_release_prep_provenance.py"
    repository = "tuanductran/soulmap-ai"
    assert 'run_head_sha=os.environ["GITHUB_SHA"]' in script.read_text()
    environment = {
        **os.environ,
        "GITHUB_REPOSITORY": repository,
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_WORKFLOW_REF": (
            "tuanductran/soulmap-ai/.github/workflows/release.yml@refs/heads/main"
        ),
        "GITHUB_WORKFLOW_SHA": "b" * 40,
        "GITHUB_SHA": "d" * 40,
        "RELEASE_BRANCH": "release/prep-123",
        "RELEASE_HEAD_SHA": "c" * 40,
    }

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release-prep-provenance.json"
        result = subprocess.run(
            [sys.executable, str(script), str(output)],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert result.returncode == 0, result.stderr
        manifest = json.loads(output.read_text(encoding="utf-8"))
        assert manifest == {
            "repository": repository,
            "run_id": 123,
            "run_attempt": 1,
            "workflow_ref": environment["GITHUB_WORKFLOW_REF"],
            "workflow_sha": "b" * 40,
            "run_head_sha": "d" * 40,
            "release_branch": "release/prep-123",
            "release_head_sha": "c" * 40,
        }

        invalid_environment = {
            **environment,
            "RELEASE_BRANCH": "release/prep-999",
        }
        invalid_result = subprocess.run(
            [sys.executable, str(script), str(output)],
            check=False,
            capture_output=True,
            text=True,
            env=invalid_environment,
        )
        assert invalid_result.returncode != 0
        invalid_sha_environment = {**environment, "GITHUB_SHA": "not-a-sha"}
        invalid_sha_result = subprocess.run(
            [sys.executable, str(script), str(output)],
            check=False,
            capture_output=True,
            text=True,
            env=invalid_sha_environment,
        )
        assert invalid_sha_result.returncode != 0


def test_release_finalize_rejects_pr_without_trusted_workflow_provenance() -> None:
    script = ROOT / "scripts" / "verify_release_finalize_provenance.py"
    merge_sha = "a" * 40
    workflow_sha = "b" * 40
    run_head_sha = "d" * 40
    release_head_sha = "c" * 40
    repository = "tuanductran/soulmap-ai"
    manifest = {
        "repository": repository,
        "run_id": 123,
        "run_attempt": 1,
        "workflow_ref": (
            "tuanductran/soulmap-ai/.github/workflows/release.yml@refs/heads/main"
        ),
        "workflow_sha": workflow_sha,
        "run_head_sha": run_head_sha,
        "release_branch": "release/prep-123",
        "release_head_sha": release_head_sha,
    }
    workflow_run = {
        "id": 123,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "path": ".github/workflows/release.yml",
        "head_branch": "main",
        "head_sha": run_head_sha,
        "conclusion": "success",
        "repository": {"full_name": repository},
    }

    def make_provenance_comment(candidate_manifest: object) -> dict[str, object]:
        return {
            "user": {"login": "tuanductran"},
            "author_association": "OWNER",
            "created_at": "2026-11-17T00:00:00Z",
            "updated_at": "2026-11-17T00:00:00Z",
            "body": (
                "<!-- soulmap-release-prep-provenance:v1 -->\n"
                + json.dumps(candidate_manifest, sort_keys=True)
            ),
        }

    valid_provenance_comments = [make_provenance_comment(manifest)]
    valid_pull_request = {
        "number": 123,
        "merged_at": "2026-11-17T00:00:00Z",
        "merge_commit_sha": merge_sha,
        "base": {
            "ref": "main",
            "repo": {"full_name": repository},
        },
        "head": {
            "ref": "release/prep-123",
            "sha": release_head_sha,
            "repo": {"full_name": repository},
        },
    }
    expected_paths = [
        ".claude-plugin/marketplace.json",
        "CHANGELOG.md",
        "SKILL.md",
        "docs/integrations/README.md",
        "docs/integrations/chatgpt-instructions.md",
        "docs/integrations/gemini-instructions.md",
        "docs/integrations/poe-system-prompt.md",
        "pyproject.toml",
        "uv.lock",
    ]
    valid_files = [{"filename": path, "status": "modified"} for path in expected_paths]

    with tempfile.TemporaryDirectory() as directory:
        pull_requests_path = Path(directory) / "associated-pull-requests.json"
        changed_files_path = Path(directory) / "release-pr-files.json"
        manifest_path = Path(directory) / "release-prep-provenance.json"
        workflow_run_path = Path(directory) / "workflow-run.json"
        provenance_comments_path = Path(directory) / "release-pr-comments.json"

        def run_guard(
            pull_requests: object = None,
            changed_files: object = None,
            candidate_manifest: dict[str, object] | None = None,
            candidate_artifact_name: str | None = None,
            candidate_run: dict[str, object] | None = None,
            candidate_comments: object = None,
        ) -> subprocess.CompletedProcess[str]:
            pull_requests_path.write_text(
                json.dumps(
                    [valid_pull_request] if pull_requests is None else pull_requests
                ),
                encoding="utf-8",
            )
            changed_files_path.write_text(
                json.dumps(valid_files if changed_files is None else changed_files),
                encoding="utf-8",
            )
            selected_manifest = (
                manifest if candidate_manifest is None else candidate_manifest
            )
            manifest_path.write_text(
                json.dumps(selected_manifest),
                encoding="utf-8",
            )
            selected_artifact_name = candidate_artifact_name or (
                "release-prep-provenance-"
                f"{selected_manifest['run_id']}-{selected_manifest['run_attempt']}"
            )
            selected_comments = (
                candidate_comments
                if candidate_comments is not None
                else [make_provenance_comment(selected_manifest)]
            )
            provenance_comments_path.write_text(
                json.dumps(selected_comments),
                encoding="utf-8",
            )
            workflow_run_path.write_text(
                json.dumps(workflow_run if candidate_run is None else candidate_run),
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(pull_requests_path),
                    merge_sha,
                    str(changed_files_path),
                    repository,
                    selected_artifact_name,
                    str(manifest_path),
                    str(provenance_comments_path),
                    str(workflow_run_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        valid_result = run_guard()
        assert valid_result.returncode == 0, valid_result.stderr
        api_shaped_path_result = run_guard(
            candidate_run={**workflow_run, "path": ".github/workflows/release.yml@main"}
        )
        assert api_shaped_path_result.returncode == 0, api_shaped_path_result.stderr
        paginated_result = run_guard(
            pull_requests=[[valid_pull_request]],
            changed_files=[valid_files],
            candidate_comments=[valid_provenance_comments],
        )
        assert paginated_result.returncode == 0, paginated_result.stderr

        assert run_guard(candidate_comments=[]).returncode == 1
        assert (
            run_guard(
                candidate_artifact_name="release-prep-provenance-123-2"
            ).returncode
            == 1
        )
        assert (
            run_guard(candidate_run={**workflow_run, "run_attempt": 2}).returncode == 1
        )
        edited_but_matching_comment = make_provenance_comment(manifest) | {
            "updated_at": "2026-11-17T00:01:00Z"
        }
        assert (
            run_guard(candidate_comments=[edited_but_matching_comment]).returncode == 0
        )
        edited_manifest_comment = make_provenance_comment(
            {**manifest, "release_head_sha": "d" * 40}
        ) | {"updated_at": "2026-11-17T00:01:00Z"}
        assert run_guard(candidate_comments=[edited_manifest_comment]).returncode == 1
        assert (
            run_guard(
                candidate_comments=[
                    make_provenance_comment(manifest)
                    | {"user": {"login": "untrusted-contributor"}}
                ]
            ).returncode
            == 1
        )
        assert (
            run_guard(
                candidate_comments=[
                    make_provenance_comment(manifest)
                    | {"author_association": "CONTRIBUTOR"}
                ]
            ).returncode
            == 1
        )
        assert (
            run_guard(
                candidate_comments=[
                    make_provenance_comment(manifest),
                    make_provenance_comment(manifest),
                ]
            ).returncode
            == 1
        )
        assert (
            run_guard(
                candidate_comments=[
                    make_provenance_comment({**manifest, "release_head_sha": "d" * 40})
                ]
            ).returncode
            == 1
        )

        invalid_run_cases = [
            {**workflow_run, "event": "pull_request"},
            {**workflow_run, "path": ".github/workflows/other.yml"},
            {**workflow_run, "head_branch": "feature/untrusted"},
            {**workflow_run, "head_sha": "e" * 40},
            {**workflow_run, "conclusion": "failure"},
            {**workflow_run, "run_attempt": 2},
            {**workflow_run, "repository": {"full_name": "fork/soulmap-ai"}},
        ]
        for invalid_run in invalid_run_cases:
            assert run_guard(candidate_run=invalid_run).returncode == 1

        assert (
            run_guard(
                candidate_manifest={**manifest, "release_head_sha": "e" * 40}
            ).returncode
            == 1
        )
        assert (
            run_guard(
                candidate_manifest={**manifest, "run_head_sha": "e" * 40}
            ).returncode
            == 1
        )
        assert (
            run_guard(
                candidate_manifest={
                    **manifest,
                    "workflow_ref": "fork/soulmap-ai/.github/workflows/release.yml@refs/heads/main",
                }
            ).returncode
            == 1
        )
        assert (
            run_guard(
                pull_requests=[
                    {
                        **valid_pull_request,
                        "head": {**valid_pull_request["head"], "sha": "d" * 40},
                    }
                ]
            ).returncode
            == 1
        )
        assert (
            run_guard(
                pull_requests=[
                    {
                        **valid_pull_request,
                        "head": {
                            **valid_pull_request["head"],
                            "ref": "release/prep-999",
                        },
                    }
                ]
            ).returncode
            == 1
        )
        assert (
            run_guard(pull_requests=[valid_pull_request, valid_pull_request]).returncode
            == 1
        )
        assert run_guard(changed_files=valid_files[:-1]).returncode == 1
        assert (
            run_guard(
                changed_files=[
                    *valid_files,
                    {"filename": "src/action/refs.py", "status": "modified"},
                ]
            ).returncode
            == 1
        )
        assert (
            run_guard(
                changed_files=[{**valid_files[0], "status": "added"}, *valid_files[1:]]
            ).returncode
            == 1
        )
        assert run_guard(changed_files=[*valid_files, valid_files[0]]).returncode == 1


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
