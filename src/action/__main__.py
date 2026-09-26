# ruff: noqa
"""GitHub operations used by SoulMap workflows."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import random
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

# fmt: off
API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
USER_AGENT = "soulmap-github-action"
MAX_RETRIES = 4
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class GitHubActionError(RuntimeError):
    """Raised when an action operation cannot be completed safely."""


class GitHubAPIError(GitHubActionError):
    """Raised when GitHub returns a non-successful HTTP response."""

    def __init__(
        self,
        method: str,
        url: str,
        status: int,
        detail: str,
        *,
        headers: object | None = None,
    ) -> None:
        self.method = method
        self.url = url
        self.status = status
        self.detail = detail
        self.headers = headers
        super().__init__(f"GitHub API {method} {url} failed with HTTP {status}: {detail}")


class GitHubClient:
    """Small standard-library client with Octokit-style request semantics.

    Octokit is GitHub's official client family, but its supported official
    implementations do not include Python. This client deliberately keeps the
    action dependency-free while adopting the useful API-client properties:
    typed request boundaries, structured HTTP errors, retries for transient
    responses, pagination, and response validation at operation boundaries.
    """

    def __init__(self, token: str) -> None:
        if not token.strip():
            raise GitHubActionError("GitHub token must not be empty.")
        self.token = token
        self.last_response_headers: dict[str, str] = {}

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: dict[str, object] | None = None,
        data: bytes | None = None,
        content_type: str | None = None,
    ) -> dict[str, object] | list[object] | None:
        body = data if payload is None else json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        }
        if body is not None:
            headers["Content-Length"] = str(len(body))
        if content_type:
            headers["Content-Type"] = content_type

        for attempt in range(MAX_RETRIES + 1):
            try:
                with urlopen(
                    Request(url, data=body, method=method, headers=headers),
                    timeout=60,
                ) as response:
                    self.last_response_headers = dict(response.headers.items())
                    if response.status == 204:
                        return None
                    raw = response.read()
                    if not raw:
                        return None
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise GitHubActionError(
                            f"GitHub API {method} {url} returned invalid JSON."
                        ) from exc
            except HTTPError as exc:
                self.last_response_headers = dict(exc.headers.items())
                detail = exc.read().decode("utf-8", errors="replace")
                if exc.code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                    time.sleep(self._retry_delay(attempt, self.last_response_headers))
                    continue
                raise GitHubAPIError(
                    method,
                    url,
                    exc.code,
                    self._safe_error_detail(detail),
                    headers=self.last_response_headers,
                ) from exc
            except URLError as exc:
                if attempt < MAX_RETRIES:
                    time.sleep(self._retry_delay(attempt, {}))
                    continue
                raise GitHubActionError(
                    f"GitHub API {method} {url} failed after retries: {exc.reason}"
                ) from exc

        raise GitHubActionError(f"GitHub API {method} {url} exhausted retries.")

    def api(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object] | list[object] | None:
        if not path.startswith("/"):
            raise GitHubActionError(f"GitHub API path must start with '/': {path!r}")
        return self.request(method, f"{API_ROOT}{path}", payload=payload)

    def paginated(
        self,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> list[object]:
        query = dict(params or {})
        query.setdefault("per_page", 100)
        page = 1
        results: list[object] = []
        while True:
            query["page"] = page
            response = self.api(
                "GET",
                f"{path}?{urlencode(query)}",
            )
            if not isinstance(response, list):
                raise GitHubActionError(
                    f"GitHub returned a non-list response for paginated {path}."
                )
            results.extend(response)
            if len(response) < int(query["per_page"]):
                return results
            page += 1

    def upload(
        self,
        upload_url: str,
        *,
        name: str,
        content: bytes,
        content_type: str,
    ) -> dict[str, object] | list[object] | None:
        base = upload_url.split("{", 1)[0]
        query = urlencode({"name": name})
        return self.request(
            "POST",
            f"{base}?{query}",
            data=content,
            content_type=content_type,
        )

    def _retry_delay(self, attempt: int, headers: dict[str, str]) -> float:
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return min(max(float(retry_after), 0.0), 30.0)
            except ValueError:
                pass
        remaining = headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            reset = headers.get("X-RateLimit-Reset")
            if reset:
                try:
                    return min(max(float(reset) - time.time(), 0.0), 30.0)
                except ValueError:
                    pass
        return min(30.0, (2**attempt) + random.uniform(0.0, 0.25))

    def _safe_error_detail(self, detail: str) -> str:
        return detail.replace(self.token, "[REDACTED]")


def env(name: str, *, required: bool = True, default: str = "") -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise GitHubActionError(f"Missing required action input: {name}")
    return value


def boolean(name: str, default: bool = False) -> bool:
    value = env(
        name,
        required=False,
        default="true" if default else "false",
    ).strip().lower()
    if value not in {"true", "false"}:
        raise GitHubActionError(f"Input {name!r} must be true or false.")
    return value == "true"


def repository_parts(repository: str) -> tuple[str, str]:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise GitHubActionError(f"Invalid GitHub repository: {repository!r}")
    return owner, name


def write_output(name: str, value: object) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with Path(output_file).open("a", encoding="utf-8") as handle:
        handle.write(f"{name}<<SOULMAP_EOF\n{value}\nSOULMAP_EOF\n")


def summary(message: str) -> None:
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with Path(summary_file).open("a", encoding="utf-8") as handle:
            handle.write(f"{message.rstrip()}\n")


def read_body() -> str:
    body = env("INPUT_BODY", required=False)
    body_path = env("INPUT_BODY_PATH", required=False)
    if body_path:
        path = Path(body_path)
        if not path.is_file():
            raise GitHubActionError(f"Body file does not exist: {path}")
        body = path.read_text(encoding="utf-8")
    return body


def asset_paths() -> list[Path]:
    paths: list[Path] = []
    for item in env("INPUT_FILES", required=False).splitlines():
        item = item.strip()
        if item:
            path = Path(item)
            if not path.is_file():
                raise GitHubActionError(f"Release asset does not exist: {path}")
            paths.append(path)
    return paths


def get_release(
    client: GitHubClient,
    owner: str,
    repo: str,
    tag: str,
) -> dict[str, object] | None:
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
    payload: dict[str, object] = {
        "tag_name": tag,
        "name": name or tag,
        "body": body,
        "draft": True,
        "prerelease": prerelease,
        "generate_release_notes": generate_notes,
    }
    try:
        response = client.api(
            "POST",
            f"/repos/{quote(owner)}/{quote(repo)}/releases",
            payload=payload,
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
    upload_url = release.get("upload_url")
    if not isinstance(upload_url, str):
        raise GitHubActionError("Release response lacks upload metadata.")
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        raise GitHubActionError("Release response contains invalid asset metadata.")
    existing = {
        asset.get("name"): asset
        for asset in assets
        if isinstance(asset, dict) and isinstance(asset.get("name"), str)
    }
    for path in paths:
        asset = existing.get(path.name)
        if asset is not None:
            state = asset.get("state")
            size = asset.get("size")
            if state not in {None, "uploaded"}:
                raise GitHubActionError(
                    f"Existing release asset {path.name!r} is not uploaded "
                    f"(state={state!r})."
                )
            file_size = path.stat().st_size
            if isinstance(size, int) and size != file_size:
                raise GitHubActionError(
                    f"Release asset {path.name!r} already exists with size "
                    f"{size}, expected {file_size}; refusing to silently "
                    "publish a different artifact under the same name."
                )
            digest = asset.get("digest")
            if isinstance(digest, str) and digest.startswith("sha256:"):
                local_digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest.removeprefix("sha256:") != local_digest:
                    raise GitHubActionError(
                        f"Release asset {path.name!r} digest does not match "
                        "the local artifact."
                    )
            print(f"Release asset already present and verified: {path.name}")
            continue
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        content = path.read_bytes()
        print(f"Uploading release asset: {path}")
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
        if isinstance(response_digest, str) and response_digest.startswith("sha256:"):
            expected_digest = hashlib.sha256(content).hexdigest()
            if response_digest.removeprefix("sha256:") != expected_digest:
                raise GitHubActionError(
                    f"GitHub reported a digest mismatch for release asset {path.name!r}."
                )


def finalize_release(
    client: GitHubClient,
    owner: str,
    repo: str,
    release: dict[str, object],
    draft: bool,
    prerelease: bool,
) -> dict[str, object]:
    release_id = release.get("id")
    if not isinstance(release_id, int):
        raise GitHubActionError("Release response lacks a valid release ID.")
    current_draft = release.get("draft") is True
    current_prerelease = release.get("prerelease") is True
    if current_draft == draft and current_prerelease == prerelease:
        return release
    response = client.api(
        "PATCH",
        f"/repos/{quote(owner)}/{quote(repo)}/releases/{release_id}",
        payload={"draft": draft, "prerelease": prerelease},
    )
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return the finalized release.")
    return response


def run_release(client: GitHubClient) -> None:
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    tag = env("INPUT_TAG")
    release = get_release(client, owner, repo, tag)
    if release is None:
        release = create_release(
            client,
            owner,
            repo,
            tag,
            env("INPUT_RELEASE_NAME", required=False, default=tag),
            read_body(),
            boolean("INPUT_PRERELEASE"),
            boolean("INPUT_GENERATE_RELEASE_NOTES"),
        )
    else:
        release = update_release_metadata(client, owner, repo, release)
    upload_assets(client, release, asset_paths())
    release = get_release(client, owner, repo, tag) or release
    release = finalize_release(
        client,
        owner,
        repo,
        release,
        boolean("INPUT_DRAFT"),
        boolean("INPUT_PRERELEASE"),
    )
    release_id, release_url = release.get("id"), release.get("html_url")
    if not isinstance(release_id, int) or not isinstance(release_url, str) or not release_url:
        raise GitHubActionError("GitHub release response is missing outputs.")
    write_output("release-id", release_id)
    write_output("release-url", release_url)
    write_output("tag-name", tag)
    summary(f"## SoulMap release published\n\n- Tag: {tag}\n- URL: {release_url}")


def run_pull_request(client: GitHubClient) -> None:
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    branch = env("INPUT_BRANCH")
    base = env("INPUT_BASE", required=False, default="main")
    tag = env("INPUT_TAG", required=False)
    title = env(
        "INPUT_TITLE",
        required=False,
        default=f"chore(release): {tag}" if tag else "chore(release)",
    )
    body = read_body() or f"Automated release preparation for {tag}."
    existing = client.paginated(
        f"/repos/{quote(owner)}/{quote(repo)}/pulls",
        params={
            "state": "open",
            "head": f"{owner}:{branch}",
            "base": base,
        },
    )
    prs = [item for item in existing if isinstance(item, dict)]
    if len(prs) > 1:
        raise GitHubActionError(
            f"GitHub returned multiple open release PRs for {owner}:{branch} -> {base}."
        )
    pr = prs[0] if prs else None
    if pr is None:
        created = client.api(
            "POST",
            f"/repos/{quote(owner)}/{quote(repo)}/pulls",
            payload={"base": base, "head": branch, "title": title, "body": body},
        )
        if not isinstance(created, dict):
            raise GitHubActionError("GitHub did not return a pull request object.")
        pr = created
    url = pr.get("html_url")
    number = pr.get("number")
    if not isinstance(url, str) or not url or not isinstance(number, int):
        raise GitHubActionError("GitHub did not return complete pull request metadata.")
    write_output("pull-request-url", url)
    write_output("pull-request-number", number)
    summary(f"## SoulMap release pull request\n\n- URL: {url}\n- Number: {number}")


def main() -> int:
    try:
        operation = env("INPUT_OPERATION").strip().lower()
        client = GitHubClient(env("INPUT_TOKEN"))
        if operation == "release":
            run_release(client)
        elif operation == "pull-request":
            run_pull_request(client)
        else:
            raise GitHubActionError(
                f"Unsupported operation {operation!r}; expected release or pull-request."
            )
    except GitHubActionError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
