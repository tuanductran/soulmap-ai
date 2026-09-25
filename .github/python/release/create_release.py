"""Create a GitHub Release and upload release assets using only Python's stdlib."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API_VERSION = "2026-03-10"
API_ROOT = "https://api.github.com"
UPLOADS_ROOT = "https://uploads.github.com"


class GitHubAPIError(RuntimeError):
    """Raised when a GitHub API operation fails."""


def _request(
    token: str,
    method: str,
    url: str,
    *,
    payload: dict[str, object] | None = None,
    content: bytes | None = None,
    content_type: str = "application/json",
) -> dict[str, object] | None:
    body = content
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "soulmap-release-finalize",
            "Content-Type": content_type,
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            if response.status == 204:
                return None
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubAPIError(
            f"GitHub API {method} {url} failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise GitHubAPIError(
            f"GitHub API {method} {url} failed: {exc.reason}"
        ) from exc


def _repository_parts(repository: str) -> tuple[str, str]:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise ValueError(f"Invalid GitHub repository: {repository!r}")
    return owner, name


def create_release(
    *,
    token: str,
    repository: str,
    tag: str,
    name: str,
    asset_paths: list[Path],
) -> None:
    owner, repo = _repository_parts(repository)
    release_url = f"{API_ROOT}/repos/{owner}/{repo}/releases"
    release = _request(
        token,
        "POST",
        release_url,
        payload={
            "tag_name": tag,
            "name": name,
            "draft": False,
            "prerelease": False,
            "generate_release_notes": False,
        },
    )
    if release is None:
        raise GitHubAPIError("GitHub did not return the created release.")

    release_id = release.get("id")
    if not isinstance(release_id, int):
        raise GitHubAPIError("GitHub did not return a release ID.")

    for asset_path in asset_paths:
        if not asset_path.is_file():
            raise FileNotFoundError(asset_path)
        asset_url = (
            f"{UPLOADS_ROOT}/repos/{owner}/{repo}/releases/{release_id}/assets"
            f"?name={quote(asset_path.name)}"
        )
        _request(
            token,
            "POST",
            asset_url,
            content=asset_path.read_bytes(),
            content_type="application/octet-stream",
        )
        print(f"Uploaded release asset {asset_path.name}.")


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("SOULMAP_RELEASE_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    tag = os.environ.get("RELEASE_TAG")
    name = os.environ.get("RELEASE_NAME") or tag
    asset_dir = Path(os.environ.get("RELEASE_ASSET_DIR", "dist"))

    missing = [
        name
        for name, value in (
            ("GITHUB_TOKEN or SOULMAP_RELEASE_TOKEN", token),
            ("GITHUB_REPOSITORY", repository),
            ("RELEASE_TAG", tag),
            ("RELEASE_NAME", name),
        )
        if not value
    ]
    if missing:
        print(
            f"Missing required release environment: {', '.join(missing)}.",
            file=sys.stderr,
        )
        return 2

    asset_names = (
        "soulmap-ai.zip",
        "soulmap-ai.skill",
        "soulmap-ai-library.json",
        "release-verification.json",
        "release-provenance.json",
    )

    try:
        create_release(
            token=token,
            repository=repository,
            tag=tag,
            name=name,
            asset_paths=[asset_dir / filename for filename in asset_names],
        )
    except (GitHubAPIError, OSError, ValueError) as exc:
        print(f"GitHub release creation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
