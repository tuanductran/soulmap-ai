"""Fail-closed validation for release finalization provenance and scope."""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED_RELEASE_PREP_FILES = frozenset(
    {
        ".claude-plugin/marketplace.json",
        "CHANGELOG.md",
        "SKILL.md",
        "docs/integrations/README.md",
        "docs/integrations/chatgpt-instructions.md",
        "docs/integrations/gemini-instructions.md",
        "docs/integrations/poe-system-prompt.md",
        "pyproject.toml",
        "uv.lock",
    }
)


def _flatten_pages(value: object) -> list[object] | None:
    if not isinstance(value, list):
        return None
    if all(isinstance(page, list) for page in value):
        return [item for page in value for item in page]
    return value


def has_valid_release_prep_provenance(
    associated_pull_requests: object,
    merge_sha: str,
    repository: str,
    changed_files: object,
) -> bool:
    pull_requests = _flatten_pages(associated_pull_requests)
    files = _flatten_pages(changed_files)
    if (
        pull_requests is None
        or files is None
        or not merge_sha
        or not repository
        or not files
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
            and isinstance(head.get("ref"), str)
            and head["ref"].startswith("release/prep-")
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
    if len(sys.argv) != 5:
        print(
            "Usage: verify_release_finalize_provenance.py "
            "<associated-prs.json> <merge-sha> <changed-files.json> <repository>",
            file=sys.stderr,
        )
        return 2

    pull_requests_path = Path(sys.argv[1])
    merge_sha = sys.argv[2]
    changed_files_path = Path(sys.argv[3])
    repository = sys.argv[4]
    try:
        associated_pull_requests = json.loads(
            pull_requests_path.read_text(encoding="utf-8")
        )
        changed_files = json.loads(changed_files_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(
            "Refusing to publish: unable to read pull-request provenance or changed files.",
            file=sys.stderr,
        )
        return 1

    if not has_valid_release_prep_provenance(
        associated_pull_requests, merge_sha, repository, changed_files
    ):
        print(
            "Refusing to publish: expected exactly one merged same-repository "
            "release/prep-* PR targeting main with the exact generated release file set.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
