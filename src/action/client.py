"""Dependency-free GitHub REST client with retry and pagination support."""

from __future__ import annotations

import json
import random
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from constants import (
    API_ROOT,
    API_VERSION,
    IDEMPOTENT_METHODS,
    MAX_RETRIES,
    RETRYABLE_STATUS_CODES,
    USER_AGENT,
)
from errors import GitHubAPIError, GitHubActionError


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
                rate_limited = bool(
                    exc.code in {403, 429}
                    and (
                        self.last_response_headers.get("Retry-After")
                        or self.last_response_headers.get("X-RateLimit-Remaining")
                        == "0"
                        or "rate limit" in detail.lower()
                    )
                )
                status_retryable = exc.code in RETRYABLE_STATUS_CODES or (
                    exc.code == 403 and rate_limited
                )
                if status_retryable and retryable and attempt < MAX_RETRIES:
                    time.sleep(
                        self._retry_delay(
                            attempt,
                            self.last_response_headers,
                            rate_limited=rate_limited,
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
                    method.upper() in IDEMPOTENT_METHODS or retry_non_idempotent
                ) and attempt < MAX_RETRIES:
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
            for parameter in parameters.split(";"):
                key, separator, value = parameter.strip().partition("=")
                if separator and key.strip().lower() == "rel":
                    relation = value.strip().strip('"').lower()
                    if relation == "next":
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
