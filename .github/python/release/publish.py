"""Publish an immutable GitHub release and upload verified artifacts through the REST API.

All GitHub release publication is intentionally performed here instead of by a
third-party release action. The workflow only supplies verified files and the
release token.
"""

from __future__ import annotations

import mimetypes
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from release_tag import _request, _repository_parts

API_VERSION = "2026-03-10"


class GitHubReleaseError(RuntimeError):
    """Raised when release publication fails."""


def _upload(
    token: str,
    url: str,
    path: Path,
) -> None:
    data = path.read_bytes()
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    request = Request(
        f"{url}?{urlencode({'name': path.name})}",
        data=data,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "Content-Type": content_type,
            "Content-Length": str(len(data)),
            "User-Agent": "soulmap-release-publisher",
        },
    )
    try:
        with urlopen(request, timeout=120) as response:
            if response.status != 201:
                raise GitHubReleaseError(
                    f"Asset upload for {path.name} returned HTTP {response.status}."
                )
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubReleaseError(
            f"Asset upload for {path.name} failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise GitHubReleaseError(
            f"Asset upload for {path.name} failed: {exc.reason}"
        ) from exc


def publish_release(
    *,
    token: str,
    repository: str,
    tag: str,
    commit_sha: str,
    artifact_dir: Path,
) -> str:
    """Create or verify a release and upload the verified artifact set."""
    owner, repo = _repository_parts(repository)
    release_path = f"/repos/{owner}/{repo}/releases/tags/{quote(tag, safe='')}"
    existing = _request(token, "GET", release_path)

    if existing is None:
        release = _request(
            token,
            "POST",
            f"/repos/{owner}/{repo}/releases",
            payload={
                "tag_name": tag,
                "target_commitish": commit_sha,
                "name": tag,
                "body": (
                    f"Automated SoulMap release {tag}.\n\n"
                    "Published only after release verification, artifact "
                    "integrity checks, and provenance generation passed."
                ),
                "draft": False,
                "prerelease": False,
                "generate_release_notes": True,
                "make_latest": "true",
            },
        )
    else:
        release = existing

    if not isinstance(release, dict):
        raise GitHubReleaseError("GitHub did not return a release object.")

    upload_url = release.get("upload_url")
    html_url = release.get("html_url")
    if not isinstance(upload_url, str):
        raise GitHubReleaseError("GitHub release response is missing publication URLs.")

    existing_assets = {
        asset.get("name")
        for asset in release.get("assets", [])
        if isinstance(asset, dict)
    }

    assets = (
        artifact_dir / "soulmap-ai.zip",
        artifact_dir / "soulmap-ai.skill",
        artifact_dir / "soulmap-ai-library.json",
        artifact_dir / "release-verification.json",
        artifact_dir / "release-provenance.json",
    )
    for asset in assets:
        if not asset.is_file():
            raise GitHubReleaseError(f"Missing verified release artifact: {asset}")
        if asset.name in existing_assets:
            print(f"Release asset already exists; keeping it: {asset.name}")
            continue
        _upload(
            token,
            upload_url.split("{", 1)[0],
            asset,
        )
        print(f"Uploaded release asset: {asset.name}")

    if not isinstance(html_url, str) or not html_url:
        raise GitHubReleaseError("GitHub release response is missing html_url.")
    return html_url


def main() -> int:
    token = os.environ.get("SOULMAP_RELEASE_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    tag = os.environ.get("RELEASE_TAG")
    commit_sha = os.environ.get("RELEASE_COMMIT")
    artifact_dir = Path(os.environ.get("RELEASE_ARTIFACT_DIR", "dist"))

    missing = [
        name
        for name, value in (
            ("SOULMAP_RELEASE_TOKEN", token),
            ("GITHUB_REPOSITORY", repository),
            ("RELEASE_TAG", tag),
            ("RELEASE_COMMIT", commit_sha),
        )
        if not value
    ]
    if missing:
        print(
            f"Missing required release environment: {', '.join(missing)}.",
            file=sys.stderr,
        )
        return 2

    assert token is not None
    assert repository is not None
    assert tag is not None
    assert commit_sha is not None

    try:
        url = publish_release(
            token=token,
            repository=repository,
            tag=tag,
            commit_sha=commit_sha,
            artifact_dir=artifact_dir,
        )
    except (GitHubReleaseError, ValueError, OSError) as exc:
        print(f"GitHub release publication failed: {exc}", file=sys.stderr)
        return 1

    print(f"Published GitHub release: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
