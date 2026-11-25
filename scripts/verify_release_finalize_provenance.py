"""Fail-closed validation for manually dispatched release provenance."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def has_valid_release_prep_provenance(
    associated_pull_requests: object, merge_sha: str
) -> bool:
    if not isinstance(associated_pull_requests, list) or not merge_sha:
        return False

    for pull_request in associated_pull_requests:
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

        base_repo_name = base_repo.get("full_name")
        if (
            pull_request.get("merged_at") is not None
            and pull_request.get("merge_commit_sha") == merge_sha
            and base.get("ref") == "main"
            and isinstance(head.get("ref"), str)
            and head["ref"].startswith("release/prep-")
            and isinstance(base_repo_name, str)
            and bool(base_repo_name)
            and head_repo.get("full_name") == base_repo_name
        ):
            return True

    return False


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: verify_release_finalize_provenance.py <response.json> <merge-sha>",
            file=sys.stderr,
        )
        return 2

    response_path = Path(sys.argv[1])
    merge_sha = sys.argv[2]
    try:
        associated_pull_requests = json.loads(response_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(
            "Refusing to publish: unable to read associated pull-request provenance.",
            file=sys.stderr,
        )
        return 1

    if not has_valid_release_prep_provenance(associated_pull_requests, merge_sha):
        print(
            "Refusing to publish: the supplied SHA is not the merge commit of a "
            "merged same-repository release/prep-* PR targeting main.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
