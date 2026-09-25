"""Create an immutable annotated Git tag through the GitHub Git Database API.

This avoids pushing a Git ref over the Git smart protocol. GitHub's REST Git
Database endpoints require Contents: write for tag objects and tag refs, so a
release commit may safely contain workflow files without requiring the token's
separate Workflows permission.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_VERSION = "2026-03-10"
API_ROOT = "https://api.github.com"


class GitHubAPIError(RuntimeError):
    """Raised when a GitHub API operation fails."""


def _request(
    token: str,
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_ROOT}{path}",
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "soulmap-release-finalize",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            if response.status == 204:
                return None
            return json.load(response)
    except HTTPError as exc:
        if exc.code == 404:
            return None
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubAPIError(
            f"GitHub API {method} {path} failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise GitHubAPIError(
            f"GitHub API {method} {path} failed: {exc.reason}"
        ) from exc


def _repository_parts(repository: str) -> tuple[str, str]:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise ValueError(f"Invalid GitHub repository: {repository!r}")
    return owner, name


def _tag_ref_path(owner: str, repo: str, tag: str) -> str:
    return f"/repos/{owner}/{repo}/git/ref/tags/{tag}"


def _resolve_commit(
    token: str,
    owner: str,
    repo: str,
    tag: str,
) -> str | None:
    """Resolve an existing tag ref to the commit it ultimately targets."""
    ref = _request(token, "GET", _tag_ref_path(owner, repo, tag))
    if ref is None:
        return None

    target = ref.get("object")
    if not isinstance(target, dict):
        raise GitHubAPIError(f"Tag ref {tag} has no Git object.")

    object_type = target.get("type")
    object_sha = target.get("sha")
    if not isinstance(object_sha, str):
        raise GitHubAPIError(f"Tag ref {tag} has no object SHA.")

    if object_type == "commit":
        return object_sha
    if object_type != "tag":
        raise GitHubAPIError(
            f"Tag ref {tag} resolves to unsupported Git object type "
            f"{object_type!r}."
        )

    tag_object = _request(
        token,
        "GET",
        f"/repos/{owner}/{repo}/git/tags/{object_sha}",
    )
    if tag_object is None:
        raise GitHubAPIError(f"Annotated tag object {object_sha} was not found.")

    target = tag_object.get("object")
    if not isinstance(target, dict) or target.get("type") != "commit":
        raise GitHubAPIError(
            f"Annotated tag {tag} does not point directly to a commit."
        )

    commit_sha = target.get("sha")
    if not isinstance(commit_sha, str):
        raise GitHubAPIError(f"Annotated tag {tag} has no commit SHA.")
    return commit_sha


def create_immutable_tag(
    *,
    token: str,
    repository: str,
    tag: str,
    commit_sha: str,
) -> None:
    """Create an annotated tag, or verify an existing immutable tag."""
    owner, repo = _repository_parts(repository)

    existing_commit = _resolve_commit(token, owner, repo, tag)
    if existing_commit is not None:
        if existing_commit != commit_sha:
            raise GitHubAPIError(
                f"Release tag {tag} already exists at {existing_commit}; "
                f"expected {commit_sha}."
            )
        print(
            f"Release tag {tag} already exists at the exact release commit; "
            "reusing it without moving it."
        )
        return

    tag_object = _request(
        token,
        "POST",
        f"/repos/{owner}/{repo}/git/tags",
        payload={
            "tag": tag,
            "message": f"Release {tag}",
            "object": commit_sha,
            "type": "commit",
            "tagger": {
                "name": "github-actions[bot]",
                "email": "github-actions[bot]@users.noreply.github.com",
                "date": datetime.now(UTC).isoformat(timespec="seconds").replace(
                    "+00:00", "Z"
                ),
            },
        },
    )
    if tag_object is None:
        raise GitHubAPIError("GitHub did not return the created tag object.")

    tag_sha = tag_object.get("sha")
    if not isinstance(tag_sha, str):
        raise GitHubAPIError("GitHub did not return the created tag object SHA.")

    try:
        _request(
            token,
            "POST",
            f"/repos/{owner}/{repo}/git/refs",
            payload={"ref": f"refs/tags/{tag}", "sha": tag_sha},
        )
    except GitHubAPIError:
        # Another publisher may have won the race. Re-read the ref and only
        # accept the race if it points to exactly the same release commit.
        existing_commit = _resolve_commit(token, owner, repo, tag)
        if existing_commit == commit_sha:
            print(
                f"Release tag {tag} was created concurrently at the exact "
                "release commit; reusing it."
            )
            return
        raise

    print(f"Created immutable annotated release tag {tag} at {commit_sha}.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--tag", default=os.environ.get("RELEASE_TAG"))
    parser.add_argument("--commit", default=os.environ.get("RELEASE_COMMIT"))
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    token = os.environ.get("SOULMAP_RELEASE_TOKEN")

    missing = [
        name
        for name, value in (
            ("SOULMAP_RELEASE_TOKEN", token),
            ("GITHUB_REPOSITORY", args.repository),
            ("RELEASE_TAG", args.tag),
            ("RELEASE_COMMIT", args.commit),
        )
        if not value
    ]
    if missing:
        print(
            f"Missing required release environment: {', '.join(missing)}.",
            file=sys.stderr
        )
        return 2

    try:
        create_immutable_tag(
            token=token,
            repository=args.repository,
            tag=args.tag,
            commit_sha=args.commit,
        )
    except (GitHubAPIError, ValueError) as exc:
        print(f"Release tag creation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
