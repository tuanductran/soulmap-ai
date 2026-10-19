"""Read-only verification of GitHub release immutability."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from constants import API_ROOT, USER_AGENT, VERIFY_API_VERSION
from errors import GitHubActionError
from inputs import env, repository_parts, summary, write_output


def run_verify_release_immutability() -> None:
    """Verify a published release through GitHub's unauthenticated public API."""
    repository = env(
        "INPUT_REPOSITORY",
        required=False,
        default=os.environ.get("GITHUB_REPOSITORY", ""),
    )
    if not repository:
        raise GitHubActionError(
            "Missing action input INPUT_REPOSITORY or GITHUB_REPOSITORY."
        )
    owner, repo = repository_parts(repository)
    tag = env("INPUT_TAG", required=False) or None
    endpoint = (
        f"/repos/{quote(owner)}/{quote(repo)}/releases/tags/{quote(tag, safe='')}"
        if tag
        else f"/repos/{quote(owner)}/{quote(repo)}/releases/latest"
    )
    request = Request(
        f"{API_ROOT}{endpoint}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": VERIFY_API_VERSION,
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            release = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubActionError(
            f"Release immutability verification failed: GitHub API GET "
            f"{endpoint} returned HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise GitHubActionError(
            f"Release immutability verification failed: GitHub API GET "
            f"{endpoint} failed: {exc.reason}"
        ) from exc

    if not isinstance(release, dict):
        raise GitHubActionError(
            "Release immutability verification failed: GitHub returned "
            "an unexpected release payload."
        )
    release_tag = release.get("tag_name")
    immutable = release.get("immutable")
    if not isinstance(release_tag, str):
        raise GitHubActionError(
            "Release immutability verification failed: release payload has no tag_name."
        )
    if immutable is not True:
        raise GitHubActionError(
            f"Release {release_tag} is not immutable (immutable={immutable!r}). "
            "Enable GitHub release immutability before treating release "
            "protection as complete."
        )

    write_output("tag-name", release_tag)
    summary(f"## Release immutability verified\n\n- Tag: {release_tag}")
    print(f"Release {release_tag} is immutable.")
