"""Fail-closed validation for release finalization provenance and scope."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EXPECTED_RELEASE_PREP_FILES = frozenset(
    {
        ".claude-plugin/marketplace.json",
        ".claude-plugin/plugin.json",
        "CHANGELOG.md",
        "SKILL.md",
        "docs/integrations/README.md",
        "pyproject.toml",
        "uv.lock",
    }
)
PROVENANCE_COMMENT_MARKER = "<!-- soulmap-release-prep-provenance:v1 -->"
_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _flatten_pages(value: object) -> list[object] | None:
    if not isinstance(value, list):
        return None
    if all(isinstance(page, list) for page in value):
        return [item for page in value for item in page]
    return value


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and _SHA_PATTERN.fullmatch(value) is not None


def _has_matching_owner_provenance_comment(
    comments: list[object],
    repository: str,
    manifest: dict[str, object],
) -> bool:
    """Require one owner-authored consistency comment matching the run artifact."""
    owner = repository.split("/", maxsplit=1)[0].casefold()
    matching_manifests: list[dict[str, object]] = []
    for item in comments:
        if not isinstance(item, dict):
            continue
        user = item.get("user")
        body = item.get("body")
        if not isinstance(user, dict) or not isinstance(body, str):
            continue
        login = user.get("login")
        if (
            not isinstance(login, str)
            or login.casefold() != owner
            or item.get("author_association") != "OWNER"
            or not body.startswith(f"{PROVENANCE_COMMENT_MARKER}\n")
        ):
            continue
        try:
            comment_manifest = json.loads(body.split("\n", maxsplit=1)[1])
        except (IndexError, json.JSONDecodeError):
            return False
        if not isinstance(comment_manifest, dict):
            return False
        if comment_manifest.get("run_id") == manifest.get(
            "run_id"
        ) and comment_manifest.get("run_attempt") == manifest.get("run_attempt"):
            matching_manifests.append(comment_manifest)

    return len(matching_manifests) == 1 and matching_manifests[0] == manifest


def has_valid_release_prep_provenance(
    associated_pull_requests: object,
    merge_sha: str,
    repository: str,
    artifact_name: str,
    changed_files: object,
    manifest: object,
    provenance_comments: object,
    workflow_run: object,
) -> bool:
    """Require a successful main-branch Release Prep run for this exact PR head."""
    pull_requests = _flatten_pages(associated_pull_requests)
    files = _flatten_pages(changed_files)
    comments = _flatten_pages(provenance_comments)
    if (
        pull_requests is None
        or files is None
        or comments is None
        or not merge_sha
        or not repository
        or not artifact_name
        or not files
        or not isinstance(manifest, dict)
        or not isinstance(workflow_run, dict)
        or not _has_matching_owner_provenance_comment(comments, repository, manifest)
    ):
        return False

    required_manifest_keys = {
        "repository",
        "run_id",
        "run_attempt",
        "workflow_ref",
        "workflow_sha",
        "run_head_sha",
        "release_branch",
        "release_head_sha",
    }
    if set(manifest) != required_manifest_keys:
        return False

    run_id = manifest.get("run_id")
    run_attempt = manifest.get("run_attempt")
    workflow_sha = manifest.get("workflow_sha")
    run_head_sha = manifest.get("run_head_sha")
    release_branch = manifest.get("release_branch")
    release_head_sha = manifest.get("release_head_sha")
    expected_workflow_ref = (
        f"{repository}/.github/workflows/release.yml@refs/heads/main"
    )
    if (
        manifest.get("repository") != repository
        or not isinstance(run_id, int)
        or isinstance(run_id, bool)
        or run_id <= 0
        or not isinstance(run_attempt, int)
        or isinstance(run_attempt, bool)
        or run_attempt <= 0
        or manifest.get("workflow_ref") != expected_workflow_ref
        or not _is_sha(workflow_sha)
        or not _is_sha(run_head_sha)
        or not isinstance(release_branch, str)
        or release_branch != f"release/prep-{run_id}"
        or not _is_sha(release_head_sha)
        or artifact_name != f"release-prep-provenance-{run_id}-{run_attempt}"
    ):
        return False

    run_repository = workflow_run.get("repository")
    if not isinstance(run_repository, dict):
        return False
    if (
        workflow_run.get("id") != run_id
        or workflow_run.get("run_attempt") != run_attempt
        or workflow_run.get("event") != "workflow_dispatch"
        or workflow_run.get("path")
        not in {
            ".github/workflows/release.yml",
            ".github/workflows/release.yml@main",
        }
        or workflow_run.get("head_branch") != "main"
        or workflow_run.get("head_sha") != run_head_sha
        or workflow_run.get("conclusion") != "success"
        or run_repository.get("full_name") != repository
    ):
        return False

    matching_pull_requests: list[dict[str, object]] = []
    for pull_request in pull_requests:
        if not isinstance(pull_request, dict):
            continue
        base = pull_request.get("base")
        head = pull_request.get("head")
        if not isinstance(base, dict) or not isinstance(head, dict):
            continue
        base_repo = base.get("repo")
        head_repo = head.get("repo")
        if not isinstance(base_repo, dict) or not isinstance(head_repo, dict):
            continue

        if (
            pull_request.get("merged_at") is not None
            and pull_request.get("merge_commit_sha") == merge_sha
            and base.get("ref") == "main"
            and base_repo.get("full_name") == repository
            and head.get("ref") == release_branch
            and head.get("sha") == release_head_sha
            and head_repo.get("full_name") == repository
        ):
            matching_pull_requests.append(pull_request)

    if len(matching_pull_requests) != 1:
        return False

    filenames: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            return False
        filename = item.get("filename")
        if not isinstance(filename, str) or item.get("status") != "modified":
            return False
        filenames.append(filename)

    return (
        len(filenames) == len(set(filenames))
        and frozenset(filenames) == EXPECTED_RELEASE_PREP_FILES
    )


def main() -> int:
    if len(sys.argv) != 9:
        print(
            "Usage: verify_release_finalize_provenance.py "
            "<associated-prs.json> <merge-sha> <changed-files.json> "
            "<repository> <provenance-artifact-name> "
            "<release-prep-manifest.json> <release-pr-comments.json> "
            "<workflow-run.json>",
            file=sys.stderr,
        )
        return 2

    pull_requests_path = Path(sys.argv[1])
    merge_sha = sys.argv[2]
    changed_files_path = Path(sys.argv[3])
    repository = sys.argv[4]
    artifact_name = sys.argv[5]
    manifest_path = Path(sys.argv[6])
    provenance_comments_path = Path(sys.argv[7])
    workflow_run_path = Path(sys.argv[8])
    try:
        associated_pull_requests = json.loads(
            pull_requests_path.read_text(encoding="utf-8")
        )
        changed_files = json.loads(changed_files_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        provenance_comments = json.loads(
            provenance_comments_path.read_text(encoding="utf-8")
        )
        workflow_run = json.loads(workflow_run_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(
            "Refusing to publish: unable to read pull-request provenance, "
            "owner consistency comment, workflow-run metadata, or changed files.",
            file=sys.stderr,
        )
        return 1

    if not has_valid_release_prep_provenance(
        associated_pull_requests,
        merge_sha,
        repository,
        artifact_name,
        changed_files,
        manifest,
        provenance_comments,
        workflow_run,
    ):
        print(
            "Refusing to publish: expected exactly one merged PR whose head "
            "matches a successful workflow_dispatch run of the trusted "
            "main-branch Release Prep workflow, an owner-authored consistency "
            "comment matching the immutable run artifact, and the exact "
            "generated release file set.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
