"""Create a run-bound manifest for trusted release preparation."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
_RUN_ID_PATTERN = re.compile(r"^[1-9][0-9]*$")


def build_release_prep_provenance(
    *,
    repository: str,
    run_id: str,
    run_attempt: str,
    workflow_ref: str,
    workflow_sha: str,
    release_branch: str,
    release_head_sha: str,
) -> dict[str, str | int]:
    """Build a manifest that binds one release branch to one workflow run."""
    if not repository or "/" not in repository:
        raise ValueError("repository must be owner/name")
    if not _RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("run_id must be a positive integer")
    if not _RUN_ID_PATTERN.fullmatch(run_attempt):
        raise ValueError("run_attempt must be a positive integer")
    if not _SHA_PATTERN.fullmatch(workflow_sha):
        raise ValueError("workflow_sha must be a full lowercase commit SHA")
    if not _SHA_PATTERN.fullmatch(release_head_sha):
        raise ValueError("release_head_sha must be a full lowercase commit SHA")

    expected_workflow_ref = (
        f"{repository}/.github/workflows/release.yml@refs/heads/main"
    )
    if workflow_ref != expected_workflow_ref:
        raise ValueError("release preparation must run from the main workflow ref")
    if release_branch != f"release/prep-{run_id}":
        raise ValueError("release branch must be derived from the workflow run ID")

    return {
        "repository": repository,
        "run_id": int(run_id),
        "run_attempt": int(run_attempt),
        "workflow_ref": workflow_ref,
        "workflow_sha": workflow_sha,
        "release_branch": release_branch,
        "release_head_sha": release_head_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    try:
        manifest = build_release_prep_provenance(
            repository=os.environ["GITHUB_REPOSITORY"],
            run_id=__import__("os").environ["GITHUB_RUN_ID"],
            run_attempt=__import__("os").environ["GITHUB_RUN_ATTEMPT"],
            workflow_ref=__import__("os").environ["GITHUB_WORKFLOW_REF"],
            workflow_sha=__import__("os").environ["GITHUB_WORKFLOW_SHA"],
            release_branch=__import__("os").environ["RELEASE_BRANCH"],
            release_head_sha=__import__("os").environ["RELEASE_HEAD_SHA"],
        )
    except (KeyError, ValueError) as error:
        parser.error(str(error))

    args.output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
