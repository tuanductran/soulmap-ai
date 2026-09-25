"""Create a GitHub pull request for an automated release branch.

The release token is intentionally supplied by the workflow rather than using
GITHUB_TOKEN: GitHub documents that pull requests created by GITHUB_TOKEN can
require workflow approval, while a PAT or GitHub App token can trigger normal
pull_request workflows automatically.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API_VERSION = "2022-11-28"
API_ROOT = "https://api.github.com"


class GitHubAPIError(RuntimeError):
    """Raised when a GitHub API operation fails."""


def _request(
    token: str,
    method: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
) -> dict[str, object] | list[object] | None:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_ROOT}{path}",
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "soulmap-release-prep",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            if response.status == 204:
                return None
            return json.load(response)
    except HTTPError as exc:
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


def create_release_pr(
    *,
    token: str,
    repository: str,
    branch: str,
    tag: str,
) -> str:
    """Create and return the URL of the release pull request."""
    owner, repo = _repository_parts(repository)
    body = (
        f"Automated release preparation for {tag}. "
        "Merge this PR only after all required CI checks pass. "
        "The merge commit will be tagged and published by the "
        "release-finalize workflow; this workflow never writes directly "
        "to main or force-moves tags."
    )
    response = _request(
        token,
        "POST",
        f"/repos/{owner}/{repo}/pulls",
        payload={
            "base": "main",
            "head": branch,
            "title": f"chore(release): {tag}",
            "body": body,
        },
    )
    if not isinstance(response, dict):
        raise GitHubAPIError("GitHub did not return a pull request object.")

    url = response.get("html_url")
    if not isinstance(url, str) or not url:
        raise GitHubAPIError("GitHub did not return a pull request URL.")

    return url


def main() -> int:
    token = os.environ.get("SOULMAP_RELEASE_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    branch = os.environ.get("RELEASE_BRANCH")
    tag = os.environ.get("RELEASE_TAG")

    missing = [
        name
        for name, value in (
            ("SOULMAP_RELEASE_TOKEN", token),
            ("GITHUB_REPOSITORY", repository),
            ("RELEASE_BRANCH", branch),
            ("RELEASE_TAG", tag),
        )
        if not value
    ]
    if missing:
        print(
            f"Missing required release environment: {', '.join(missing)}.",
            file=sys.stderr,
        )
        return 2

    try:
        url = create_release_pr(
            token=token,
            repository=repository,
            branch=branch,
            tag=tag,
        )
    except (GitHubAPIError, ValueError) as exc:
        print(f"Release pull request creation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Created release pull request: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
