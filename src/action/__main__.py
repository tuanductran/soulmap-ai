"""Entry point for the SoulMap GitHub Action."""

from __future__ import annotations

import sys

from client import GitHubClient
from errors import GitHubActionError
from inputs import env
from operations import run_branch, run_pull_request, run_release, run_tag
from verify import run_verify_release_immutability


def main() -> int:
    """Run the selected GitHub operation and report action failures."""
    try:
        operation = env("INPUT_OPERATION").strip().lower()
        if operation == "verify-release-immutability":
            run_verify_release_immutability()
        elif operation in {"release", "branch", "pull-request", "tag"}:
            client = GitHubClient(env("INPUT_TOKEN"))
            if operation == "release":
                run_release(client)
            elif operation == "branch":
                run_branch(client)
            elif operation == "pull-request":
                run_pull_request(client)
            else:
                run_tag(client)
        else:
            raise GitHubActionError(
                "Unsupported operation "
                f"{operation!r}; expected release, pull-request, tag, branch, "
                "or verify-release-immutability."
            )
    except GitHubActionError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
