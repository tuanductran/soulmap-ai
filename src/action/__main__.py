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

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
USER_AGENT = "soulmap-github-action"
MAX_RETRIES = 4
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
IDEMPOTENT_METHODS = {"DELETE", "GET", "HEAD", "PATCH", "PUT"}


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
        """Initialize a structured GitHub API error."""
        self.method = method
        self.url = url
        self.status = status
        self.detail = detail
        self.headers = headers
        super().__init__(
            f"GitHub API {method} {url} failed with HTTP {status}: {detail}"
        )


class GitHubClient:
    """Small standard-library client with Octokit-style request semantics.

    Octokit is GitHub's official client family, but its supported official
    implementations do not include Python. This client deliberately keeps the
    action dependency-free while adopting the useful API-client properties:
    typed request boundaries, structured HTTP errors, retries for transient
    responses, pagination, and response validation at operation boundaries.
    """

    def __init__(self, token: str) -> None:
        """Initialize the client with a GitHub API token."""
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
        retry_non_idempotent: bool = False,
    ) -> dict[str, object] | list[object] | None:
        """Send an authenticated REST request and decode its JSON response."""
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
                retryable = method.upper() in IDEMPOTENT_METHODS or retry_non_idempotent
                rate_limited = exc.code in {403, 429} and (
                        self.last_response_headers.get("Retry-After")
                        or self.last_response_headers.get("X-RateLimit-Remaining")
                        == "0"
                        or "rate limit" in detail.lower()
                    )
                status_retryable = exc.code in RETRYABLE_STATUS_CODES or (
                    exc.code == 403 and rate_limited
                )
                if status_retryable and retryable and attempt < MAX_RETRIES:
                    time.sleep(
                        self._retry_delay(
                            attempt,
                            self.last_response_headers,
                            rate_limited=bool(rate_limited),
                        )
                    )
                    continue
                raise GitHubAPIError(
                    method,
                    url,
                    exc.code,
                    self._safe_error_detail(detail),
                    headers=self.last_response_headers,
                ) from exc
            except URLError as exc:
                if (
                    (method.upper() in IDEMPOTENT_METHODS or retry_non_idempotent)
                    and attempt < MAX_RETRIES
                ):
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
        """Send a request to the GitHub REST API root."""
        if not path.startswith("/"):
            raise GitHubActionError(f"GitHub API path must start with '/': {path!r}")
        return self.request(method, f"{API_ROOT}{path}", payload=payload)

    def paginated(
        self,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
    ) -> list[object]:
        """Collect all list items by following GitHub Link headers."""
        query = dict(params or {})
        query.setdefault("per_page", 100)
        next_url = f"{API_ROOT}{path}?{urlencode(query)}"
        results: list[object] = []
        while next_url:
            response = self.request("GET", next_url)
            if not isinstance(response, list):
                raise GitHubActionError(
                    f"GitHub returned a non-list response for paginated {path}."
                )
            results.extend(response)
            next_url = self._next_link(self.last_response_headers.get("Link"))
        return results

    @staticmethod
    def _next_link(link_header: str | None) -> str:
        if not link_header:
            return ""
        for link in link_header.split(","):
            target, _, parameters = link.partition(";")
            relation = next(
                (
                    value.strip().strip('"').lower()
                    for value in parameters.split(";")
                    if value.strip().lower().startswith("rel=")
                ),
                "",
            )
            if relation == "rel="next"" or relation == "rel=next":
                target = target.strip()
                if target.startswith("<") and target.endswith(">"):
                    return target[1:-1]
        return ""

    def upload(
        self,
        upload_url: str,
        *,
        name: str,
        content: bytes,
        content_type: str,
    ) -> dict[str, object] | list[object] | None:
        """Upload raw release-asset bytes to GitHub's hypermedia URL."""
        base = upload_url.split("{", 1)[0]
        query = urlencode({"name": name})
        return self.request(
            "POST",
            f"{base}?{query}",
            data=content,
            content_type=content_type,
        )

    def list_release_assets(self, assets_url: str) -> list[object]:
        """List all assets for a release using its hypermedia URL."""
        next_url = f"{assets_url}?per_page=100"
        results: list[object] = []
        while next_url:
            response = self.request("GET", next_url)
            if not isinstance(response, list):
                raise GitHubActionError(
                    "GitHub returned invalid release asset metadata.",
                )
            results.extend(response)
            next_url = self._next_link(self.last_response_headers.get("Link"))
        return results

    def delete_release_asset(self, asset_url: str) -> None:
        """Delete a release asset, including a failed starter upload."""
        response = self.request("DELETE", asset_url)
        if response is not None:
            raise GitHubActionError("GitHub returned content for asset deletion.")

    def _retry_delay(
        self,
        attempt: int,
        headers: dict[str, str],
        *,
        rate_limited: bool = False,
    ) -> float:
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        if headers.get("X-RateLimit-Remaining") == "0":
            reset = headers.get("X-RateLimit-Reset")
            if reset:
                try:
                    return max(float(reset) - time.time(), 0.0)
                except ValueError:
                    pass
        if rate_limited:
            return 60.0 * (2**attempt)
        return min(30.0, (2**attempt) + random.uniform(0.0, 0.25))

    def _safe_error_detail(self, detail: str) -> str:
        return detail.replace(self.token, "[REDACTED]")


def env(name: str, *, required: bool = True, default: str = "") -> str:
    """Read and validate an action environment input."""
    value = os.environ.get(name, default)
    if required and not value:
        raise GitHubActionError(f"Missing required action input: {name}")
    return value


def boolean(name: str, default: bool = False) -> bool:
    """Read an action input that must contain a boolean value."""
    value = (
        env(
            name,
            required=False,
            default="true" if default else "false",
        )
        .strip()
        .lower()
    )
    if value not in {"true", "false"}:
        raise GitHubActionError(f"Input {name!r} must be true or false.")
    return value == "true"


def repository_parts(repository: str) -> tuple[str, str]:
    """Split and validate a GitHub owner/repository identifier."""
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise GitHubActionError(f"Invalid GitHub repository: {repository!r}")
    return owner, name


def write_output(name: str, value: object) -> None:
    """Write an action output using GitHub's multiline protocol."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with Path(output_file).open("a", encoding="utf-8") as handle:
        handle.write(f"{name}<<SOULMAP_EOF\n{value}\nSOULMAP_EOF\n")


def summary(message: str) -> None:
    """Append a message to the GitHub Actions step summary."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with Path(summary_file).open("a", encoding="utf-8") as handle:
            handle.write(f"{message.rstrip()}\n")


def read_body() -> str:
    """Read the release or pull-request body from input or a file."""
    body = env("INPUT_BODY", required=False)
    body_path = env("INPUT_BODY_PATH", required=False)
    if body_path:
        path = Path(body_path)
        if not path.is_file():
            raise GitHubActionError(f"Body file does not exist: {path}")
        body = path.read_text(encoding="utf-8")
    return body


def asset_paths() -> list[Path]:
    """Resolve and validate newline-separated release asset paths."""
    paths: list[Path] = []
    for item in env("INPUT_FILES", required=False).splitlines():
        item = item.strip()
        if item:
            path = Path(item)
            if not path.is_file():
                raise GitHubActionError(f"Release asset does not exist: {path}")
            paths.append(path)
    return paths


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
    response = client.api(
        "PATCH",
        f"/repos/{quote(owner)}/{quote(repo)}/releases/{release_id}",
        payload={"draft": draft, "prerelease": prerelease},
    )
    if not isinstance(response, dict):
        raise GitHubActionError("GitHub did not return the finalized release.")
    return response


def run_release(client: GitHubClient) -> None:
    """Execute the complete release publication workflow."""
    owner, repo = repository_parts(env("INPUT_REPOSITORY"))
    tag = env("INPUT_TAG")
    ensure_tag_exists(client, owner, repo, tag)
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
    if (
        not isinstance(release_id, int)
        or not isinstance(release_url, str)
        or not release_url
    ):
        raise GitHubActionError("GitHub release response is missing outputs.")
    write_output("release-id", release_id)
    write_output("release-url", release_url)
    write_output("tag-name", tag)
    summary(f"## SoulMap release published\n\n- Tag: {tag}\n- URL: {release_url}")


def run_pull_request(client: GitHubClient) -> None:
    """Create or reuse the release preparation pull request."""
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
    """Run the selected GitHub operation and report action failures."""
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
