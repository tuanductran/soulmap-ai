"""Verify that a published GitHub release is immutable.

This is an operational audit for repository-level release protection. GitHub's
public release API exposes the immutable flag, so no privileged token is
required for public repositories.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"


class ReleaseVerificationError(RuntimeError):
    """Raised when a release cannot be verified as immutable."""


def _repository_parts(repository: str) -> tuple[str, str]:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise ValueError(f"Invalid GitHub repository: {repository!r}")
    return owner, name


def _fetch_release(repository: str, tag: str | None) -> dict[str, object]:
    owner, repo = _repository_parts(repository)
    endpoint = (
        f"/repos/{owner}/{repo}/releases/tags/{tag}"
        if tag
        else f"/repos/{owner}/{repo}/releases/latest"
    )
    request = Request(
        f"{API_ROOT}{endpoint}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "soulmap-release-immutability-audit",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ReleaseVerificationError(
            f"GitHub API GET {endpoint} failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise ReleaseVerificationError(
            f"GitHub API GET {endpoint} failed: {exc.reason}"
        ) from exc

    if not isinstance(payload, dict):
        raise ReleaseVerificationError("GitHub returned an unexpected release payload.")
    return payload


def verify_release_immutable(repository: str, tag: str | None) -> None:
    release = _fetch_release(repository, tag)
    release_tag = release.get("tag_name")
    immutable = release.get("immutable")

    if not isinstance(release_tag, str):
        raise ReleaseVerificationError("Release payload has no tag_name.")
    if immutable is not True:
        raise ReleaseVerificationError(
            f"Release {release_tag} is not immutable (immutable={immutable!r}). "
            "Enable GitHub release immutability before treating release protection "
            "as complete."
        )

    print(f"Release {release_tag} is immutable.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="GitHub repository in owner/name form.",
    )
    parser.add_argument(
        "--tag",
        default=os.environ.get("RELEASE_TAG"),
        help="Release tag to verify; defaults to the latest published release.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.repository:
        print("Missing --repository or GITHUB_REPOSITORY.", file=sys.stderr)
        return 2

    try:
        verify_release_immutable(args.repository, args.tag)
    except (ReleaseVerificationError, ValueError) as exc:
        print(f"Release immutability verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
