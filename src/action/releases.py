"""GitHub Release creation, metadata, and asset operations."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import quote

from client import GitHubClient
from constants import API_ROOT
from errors import GitHubActionError, GitHubAPIError
from inputs import boolean, env, read_body


def get_release(
    client: GitHubClient,
    owner: str,
    repo: str,
    tag: str,
) -> dict[str, object] | None:
    """Return the release for a tag, or None when it does not exist."""
    path = f"/repos/{quote(owner)}/{quote(repo)}/releases/tags/{quote(tag, safe='')}"
    try:
        response = client.api("GET", path)
    except GitHubAPIError as exc:
        if exc.status == 404:
            return None
        raise
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub returned an invalid release object.")
    return response


def create_release(
    client: GitHubClient,
    owner: str,
    repo: str,
    tag: str,
    name: str,
    body: str,
    prerelease: bool,
    generate_notes: bool,
) -> dict[str, object]:
    """Create a draft release and reconcile concurrent creation safely."""
    payload: dict[str, object] = {
        "tag_name": tag,
        "name": name or tag,
        "body": body,
        "draft": True,
        "prerelease": prerelease,
        "generate_release_notes": generate_notes,
    }
    try:
        response = client.request(
            "POST",
            f"{API_ROOT}/repos/{quote(owner)}/{quote(repo)}/releases",
            payload=payload,
            retry_non_idempotent=True,
        )
    except GitHubAPIError as exc:
        # A concurrent invocation may have created the release after our GET.
        if exc.status == 422:
            existing = get_release(client, owner, repo, tag)
            if existing is not None:
                return existing
        raise
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return a release object.")
    return response


def update_release_metadata(
    client: GitHubClient,
    owner: str,
    repo: str,
    release: dict[str, object],
) -> dict[str, object]:
    """Converge mutable release metadata to the requested action inputs."""
    release_id = release.get("id")
    if not isinstance(release_id, int):
        raise GitHubActionError("Release response lacks a valid release ID.")
    desired_name = env("INPUT_RELEASE_NAME", required=False)
    desired_body = read_body()
    desired_prerelease = boolean("INPUT_PRERELEASE")
    current_prerelease = release.get("prerelease") is True
    payload: dict[str, object] = {}
    if desired_name:
        payload["name"] = desired_name
    if desired_body:
        payload["body"] = desired_body
    if desired_prerelease != current_prerelease:
        payload["prerelease"] = desired_prerelease
    if not payload:
        return release
    if release.get("immutable") is True:
        raise GitHubActionError(
            "GitHub release is immutable and cannot be updated by this action."
        )
    response = client.api(
        "PATCH",
        f"/repos/{quote(owner)}/{quote(repo)}/releases/{release_id}",
        payload=payload,
    )
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return the updated release.")
    return response


def upload_assets(
    client: GitHubClient,
    release: dict[str, object],
    paths: list[Path],
) -> None:
    """Upload and cryptographically verify each requested release asset."""
    upload_url = release.get("upload_url")
    assets_url = release.get("assets_url")
    if not isinstance(upload_url, str) or not isinstance(assets_url, str):
        raise GitHubActionError("Release response lacks upload metadata.")
    if release.get("immutable") is True and paths:
        raise GitHubActionError(
            "GitHub release is immutable and cannot accept new release assets."
        )
    seen_names: set[str] = set()
    for path in paths:
        if path.name in seen_names:
            raise GitHubActionError(
                f"Duplicate release asset filename in action input: {path.name!r}."
            )
        seen_names.add(path.name)
        content = path.read_bytes()
        expected_digest = hashlib.sha256(content).hexdigest()
        assets = client.list_release_assets(assets_url)
        existing = {
            asset.get("name"): asset
            for asset in assets
            if isinstance(asset, dict) and isinstance(asset.get("name"), str)
        }
        asset = existing.get(path.name)
        if asset is not None:
            state = asset.get("state")
            if state == "starter":
                asset_url = asset.get("url")
                if not isinstance(asset_url, str):
                    raise GitHubActionError(
                        f"GitHub returned an invalid starter asset for {path.name!r}."
                    )
                client.delete_release_asset(asset_url)
                asset = None
            elif state not in {None, "uploaded"}:
                raise GitHubActionError(
                    f"Existing release asset {path.name!r} is not uploaded "
                    f"(state={state!r})."
                )
        if asset is not None:
            size = asset.get("size")
            file_size = path.stat().st_size
            digest = asset.get("digest")
            if isinstance(size, int) and size != file_size:
                raise GitHubActionError(
                    f"Release asset {path.name!r} already exists with size "
                    f"{size}, expected {file_size}; refusing to silently "
                    "publish a different artifact under the same name."
                )
            if isinstance(digest, str) and digest.startswith("sha256:"):
                if digest.removeprefix("sha256:") != expected_digest:
                    raise GitHubActionError(
                        f"Release asset {path.name!r} digest does not match "
                        "the local artifact."
                    )
            elif asset.get("state") == "uploaded":
                raise GitHubActionError(
                    f"Release asset {path.name!r} has no verifiable SHA-256 digest."
                )
            print(f"Release asset already present and verified: {path.name}")
            continue

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        print(f"Uploading release asset: {path}")
        try:
            response = client.upload(
                upload_url,
                name=path.name,
                content=content,
                content_type=content_type,
            )
        except GitHubAPIError as exc:
            if exc.status not in {422, 500, 502, 503, 504}:
                raise
            refreshed_assets = client.list_release_assets(assets_url)
            candidate = next(
                (
                    item
                    for item in refreshed_assets
                    if isinstance(item, dict) and item.get("name") == path.name
                ),
                None,
            )
            if isinstance(candidate, dict) and candidate.get("state") == "uploaded":
                digest = candidate.get("digest")
                size = candidate.get("size")
                if (
                    size == len(content)
                    and isinstance(digest, str)
                    and digest == f"sha256:{expected_digest}"
                ):
                    print(
                        f"Release asset upload confirmed after HTTP {exc.status}: {path.name}"
                    )
                    continue
                raise GitHubActionError(
                    f"Release asset {path.name!r} exists after failed upload but "
                    "does not match the local artifact."
                ) from exc
            if isinstance(candidate, dict) and candidate.get("state") == "starter":
                asset_id = candidate.get("id")
                asset_url = candidate.get("url")
                if not isinstance(asset_id, int) or not isinstance(asset_url, str):
                    raise GitHubActionError(
                        f"GitHub returned an invalid starter asset for {path.name!r}."
                    ) from exc
                client.delete_release_asset(asset_url)
            elif exc.status == 422:
                raise GitHubActionError(
                    f"Release asset {path.name!r} appeared concurrently and "
                    "could not be reconciled safely."
                ) from exc
            else:
                raise
            response = client.upload(
                upload_url,
                name=path.name,
                content=content,
                content_type=content_type,
            )
        if not isinstance(response, dict) or response.get("name") != path.name:
            raise GitHubActionError(
                f"GitHub did not confirm upload of release asset {path.name!r}."
            )
        response_digest = response.get("digest")
        if (
            not isinstance(response_digest, str)
            or response_digest != f"sha256:{expected_digest}"
        ):
            raise GitHubActionError(
                f"GitHub did not return a verifiable SHA-256 digest for {path.name!r}."
            )


def finalize_release(
    client: GitHubClient,
    owner: str,
    repo: str,
    release: dict[str, object],
    draft: bool,
    prerelease: bool,
) -> dict[str, object]:
    """Publish or retain a release according to the requested final state."""
    release_id = release.get("id")
    if not isinstance(release_id, int):
        raise GitHubActionError("Release response lacks a valid release ID.")
    current_draft = release.get("draft") is True
    current_prerelease = release.get("prerelease") is True
    if current_draft == draft and current_prerelease == prerelease:
        return release
    if release.get("immutable") is True:
        raise GitHubActionError(
            "GitHub release is immutable and cannot be finalized by this action."
        )
    response = client.api(
        "PATCH",
        f"/repos/{quote(owner)}/{quote(repo)}/releases/{release_id}",
        payload={"draft": draft, "prerelease": prerelease},
    )
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return the finalized release.")
    return response
