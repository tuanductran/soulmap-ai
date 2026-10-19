"""Git tag and branch publication operations."""

from __future__ import annotations

import base64
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

from client import GitHubClient
from constants import API_ROOT
from errors import GitHubAPIError, GitHubActionError


def create_tag(
    client: GitHubClient,
    owner: str,
    repo: str,
    tag: str,
    target_sha: str,
) -> None:
    """Create an immutable annotated tag through GitHub's Git database API."""
    if not target_sha or len(target_sha) != 40:
        raise GitHubActionError("Tag target must be a full 40-character commit SHA.")
    ref_path = f"/repos/{quote(owner)}/{quote(repo)}/git/ref/tags/{quote(tag, safe='')}"
    try:
        existing = client.api("GET", ref_path)
    except GitHubAPIError as exc:
        if exc.status != 404:
            raise
        existing = None

    if existing is not None:
        if not isinstance(existing, dict):
            raise GitHubActionError("GitHub returned invalid tag reference metadata.")
        resolved = existing.get("object")
        if not isinstance(resolved, dict):
            raise GitHubActionError("GitHub tag reference lacks object metadata.")
        object_type = resolved.get("type")
        object_sha = resolved.get("sha")
        if object_type == "commit" and object_sha == target_sha:
            print(f"Release tag {tag} already exists at the expected commit.")
            return
        if object_type == "tag" and isinstance(object_sha, str):
            tag_object = client.api(
                "GET",
                f"/repos/{quote(owner)}/{quote(repo)}/git/tags/{quote(object_sha)}",
            )
            tag_target = (
                tag_object.get("object") if isinstance(tag_object, dict) else None
            )
            if isinstance(tag_target, dict) and tag_target.get("sha") == target_sha:
                print(f"Release tag {tag} already exists at the expected commit.")
                return
        raise GitHubActionError(
            f"Release tag {tag!r} already exists but does not point to {target_sha}."
        )

    tag_object = client.request(
        "POST",
        f"{API_ROOT}/repos/{quote(owner)}/{quote(repo)}/git/tags",
        payload={
            "tag": tag,
            "message": f"Release {tag}",
            "object": target_sha,
            "type": "commit",
            "tagger": {
                "name": "github-actions[bot]",
                "email": "41898282+github-actions[bot]@users.noreply.github.com",
                "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        },
        retry_non_idempotent=True,
    )
    if not isinstance(tag_object, dict) or not isinstance(tag_object.get("sha"), str):
        raise GitHubActionError("GitHub did not return a valid annotated tag object.")

    try:
        created_ref = client.request(
            "POST",
            f"{API_ROOT}/repos/{quote(owner)}/{quote(repo)}/git/refs",
            payload={"ref": f"refs/tags/{tag}", "sha": tag_object["sha"]},
            retry_non_idempotent=True,
        )
    except GitHubAPIError as exc:
        if exc.status not in {409, 422}:
            raise
        existing = client.api("GET", ref_path)
        if not isinstance(existing, dict):
            raise GitHubActionError(
                "GitHub returned invalid tag metadata after concurrent creation."
            ) from exc
        resolved = existing.get("object")
        if not isinstance(resolved, dict):
            raise GitHubActionError(
                "GitHub tag reference lacks object metadata after concurrent creation."
            ) from exc
        object_type = resolved.get("type")
        object_sha = resolved.get("sha")
        if object_type == "commit" and object_sha == target_sha:
            return
        if object_type == "tag" and isinstance(object_sha, str):
            existing_tag = client.api(
                "GET",
                f"/repos/{quote(owner)}/{quote(repo)}/git/tags/{quote(object_sha)}",
            )
            tag_target = (
                existing_tag.get("object") if isinstance(existing_tag, dict) else None
            )
            if isinstance(tag_target, dict) and tag_target.get("sha") == target_sha:
                return
        raise GitHubActionError(
            f"Concurrent release tag {tag!r} does not point to {target_sha}."
        ) from exc
    if (
        not isinstance(created_ref, dict)
        or created_ref.get("ref") != f"refs/tags/{tag}"
    ):
        raise GitHubActionError("GitHub did not confirm creation of the release tag.")


def create_branch(
    client: GitHubClient,
    owner: str,
    repo: str,
    branch: str,
    target_sha: str,
) -> None:
    """Create or verify a branch reference for an exact commit SHA."""
    if not target_sha or len(target_sha) != 40:
        raise GitHubActionError("Branch target must be a full 40-character commit SHA.")
    ref_path = (
        f"/repos/{quote(owner)}/{quote(repo)}/git/ref/heads/{quote(branch, safe='')}"
    )
    try:
        existing = client.api("GET", ref_path)
    except GitHubAPIError as exc:
        if exc.status != 404:
            raise
        existing = None

    if existing is not None:
        if not isinstance(existing, dict):
            raise GitHubActionError(
                "GitHub returned invalid branch reference metadata."
            )
        resolved = existing.get("object")
        if not isinstance(resolved, dict) or resolved.get("sha") != target_sha:
            raise GitHubActionError(
                f"Release branch {branch!r} already exists but does not point to {target_sha}."
            )
        print(f"Release branch {branch} already exists at the expected commit.")
        return

    # Docker actions run as root while the checked-out workspace is owned by
    # the runner user. Explicitly trust only the mounted workspace so Git's
    # dubious-ownership protection does not reject read-only and push commands.
    workspace = os.environ.get("GITHUB_WORKSPACE", str(Path.cwd()))
    environment = os.environ.copy()
    environment["GIT_CONFIG_COUNT"] = "1"
    environment["GIT_CONFIG_KEY_0"] = "safe.directory"
    environment["GIT_CONFIG_VALUE_0"] = workspace

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    ).stdout.strip()
    if head != target_sha:
        raise GitHubActionError(
            f"Local HEAD {head!r} does not match requested branch target {target_sha!r}."
        )

    encoded = base64.b64encode(f"x-access-token:{client.token}".encode()).decode(
        "ascii"
    )
    environment["GIT_CONFIG_COUNT"] = "2"
    environment["GIT_CONFIG_KEY_1"] = "http.extraheader"
    environment["GIT_CONFIG_VALUE_1"] = f"AUTHORIZATION: basic {encoded}"
    try:
        subprocess.run(
            ["git", "push", "origin", f"HEAD:refs/heads/{branch}"],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = (
            exc.stderr.strip()
            if isinstance(exc, subprocess.CalledProcessError)
            else str(exc)
        )
        raise GitHubActionError(
            f"Failed to publish release branch {branch!r}: {detail}"
        ) from exc


def ensure_tag_exists(
    client: GitHubClient,
    owner: str,
    repo: str,
    tag: str,
) -> None:
    """Require the requested Git tag to already exist before publishing."""
    path = f"/repos/{quote(owner)}/{quote(repo)}/git/ref/tags/{quote(tag, safe='')}"
    try:
        response = client.api("GET", path)
    except GitHubAPIError as exc:
        if exc.status == 404:
            raise GitHubActionError(
                f"Git tag {tag!r} does not exist; refusing to create a release from an implicit tag."
            ) from exc
        raise
    if not isinstance(response, dict) or response.get("ref") != f"refs/tags/{tag}":
        raise GitHubActionError(f"GitHub returned invalid tag metadata for {tag!r}.")
