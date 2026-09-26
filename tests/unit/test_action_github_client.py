from __future__ import annotations

import importlib.util
import io
import json
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).parents[2]
ACTION_PATH = ROOT / "src" / "action" / "__main__.py"

_spec = importlib.util.spec_from_file_location("soulmap_action", ACTION_PATH)
assert _spec is not None
assert _spec.loader is not None
action = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(action)


class FakeResponse:
    def __init__(self, payload: object, headers: dict[str, str] | None = None) -> None:
        """Create a minimal context-manager-compatible HTTP response."""
        self.status = 200
        self.headers = headers or {}
        self._payload = json.dumps(payload).encode()

    def __enter__(self) -> FakeResponse:
        """Enter the response context manager."""
        return self

    def __exit__(self, *_args: object) -> None:
        """Exit the response context manager without suppressing errors."""
        return

    def read(self) -> bytes:
        return self._payload


def test_repository_parts_rejects_malformed_repositories() -> None:
    assert action.repository_parts("tuanductran/soulmap-ai") == (
        "tuanductran",
        "soulmap-ai",
    )
    for value in ("", "owner", "/repo", "owner/", "owner/a/b"):
        try:
            action.repository_parts(value)
        except action.GitHubActionError:
            pass
        else:
            raise AssertionError(f"expected invalid repository: {value!r}")


def test_api_error_preserves_status_and_redacts_token() -> None:
    token = "secret-token"
    headers = Message()
    headers["X-RateLimit-Remaining"] = "0"
    error = HTTPError(
        "https://api.github.com/repos/a/b",
        403,
        "Forbidden",
        headers,
        io.BytesIO(json.dumps({"message": f"token={token}"}).encode()),
    )
    client = action.GitHubClient(token)

    with (
        patch.object(action, "urlopen", side_effect=error),
        pytest.raises(action.GitHubAPIError) as captured,
    ):
        client.api("GET", "/repos/a/b")

    exc = captured.value
    assert exc.status == 403
    assert token not in str(exc)
    assert "[REDACTED]" in exc.detail


def test_transient_http_error_is_retried() -> None:
    error = HTTPError(
        "https://api.github.com/repos/a/b",
        503,
        "Unavailable",
        Message(),
        __import__("io").BytesIO(b'{"message":"try again"}'),
    )
    responses = [error, FakeResponse({"ok": True})]
    client = action.GitHubClient("token")

    with (
        patch.object(action, "urlopen", side_effect=responses),
        patch.object(action.time, "sleep") as sleep,
    ):
        assert client.api("GET", "/repos/a/b") == {"ok": True}
        assert sleep.call_count == 1


def test_paginated_requests_follow_link_header() -> None:
    client = action.GitHubClient("token")
    first_page = [{"number": 1}]
    second_page = [{"number": 2}]
    responses = iter([first_page, second_page])

    def request(_method: str, url: str) -> list[object]:
        client.last_response_headers = (
            {"Link": "<https://api.github.com/next>; rel="next""}
            if "page=1" in url
            else {}
        )
        return next(responses)

    with patch.object(client, "request", side_effect=request):
        assert client.paginated("/repos/a/b/pulls", params={"state": "open"}) == [
            *first_page,
            *second_page,
        ]


def test_non_idempotent_requests_do_not_retry_by_default() -> None:
    error = HTTPError(
        "https://api.github.com/repos/a/b",
        503,
        "Unavailable",
        Message(),
        io.BytesIO(b'{"message":"try again"}'),
    )
    client = action.GitHubClient("token")

    with (
        patch.object(action, "urlopen", side_effect=error) as urlopen,
        patch.object(action.time, "sleep") as sleep,
        pytest.raises(action.GitHubAPIError),
    ):
        client.api("POST", "/repos/a/b/releases")

    assert urlopen.call_count == 1
    sleep.assert_not_called()


def test_rate_limit_retry_uses_reset_window() -> None:
    headers = Message()
    headers["X-RateLimit-Remaining"] = "0"
    headers["X-RateLimit-Reset"] = str(int(action.time.time()) + 120)
    error = HTTPError(
        "https://api.github.com/repos/a/b",
        429,
        "Too Many Requests",
        headers,
        io.BytesIO(b'{"message":"rate limit"}'),
    )
    client = action.GitHubClient("token")

    with (
        patch.object(action, "urlopen", side_effect=[error, FakeResponse({"ok": True})]),
        patch.object(action.time, "sleep") as sleep,
    ):
        assert client.api("GET", "/repos/a/b") == {"ok": True}

    assert sleep.call_count == 1
    assert sleep.call_args.args[0] >= 119


def test_asset_upload_requires_github_confirmation(tmp_path: Path) -> None:
    asset = tmp_path / "artifact.zip"
    asset.write_bytes(b"artifact")
    client = action.GitHubClient("token")
    release = {
        "upload_url": "https://uploads.github.com/repos/a/b/releases/1/assets{?name,label}",
        "assets": [],
    }

    with (
        patch.object(client, "upload", return_value={"name": "other.zip"}),
        pytest.raises(action.GitHubActionError) as captured,
    ):
        action.upload_assets(client, release, [asset])
    assert "artifact.zip" in str(captured.value)


def test_existing_asset_with_different_digest_is_rejected(tmp_path: Path) -> None:
    asset = tmp_path / "artifact.zip"
    asset.write_bytes(b"new")
    client = action.GitHubClient("token")
    release = {
        "upload_url": "https://uploads.github.com/repos/a/b/releases/1/assets{?name,label}",
        "assets": [
            {
                "name": "artifact.zip",
                "size": 3,
                "state": "uploaded",
                "digest": "sha256:" + ("0" * 64),
            }
        ],
    }

    with pytest.raises(action.GitHubActionError) as captured:
        action.upload_assets(client, release, [asset])
    assert "digest does not match" in str(captured.value)


def test_existing_asset_with_different_size_is_rejected(tmp_path: Path) -> None:
    asset = tmp_path / "artifact.zip"
    asset.write_bytes(b"new")
    client = action.GitHubClient("token")
    release = {
        "upload_url": "https://uploads.github.com/repos/a/b/releases/1/assets{?name,label}",
        "assets": [{"name": "artifact.zip", "size": 99, "state": "uploaded"}],
    }

    with pytest.raises(action.GitHubActionError) as captured:
        action.upload_assets(client, release, [asset])
    assert "refusing to silently publish" in str(captured.value)


def test_pull_request_contract_requires_complete_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = action.GitHubClient("token")
    monkeypatch.setenv("INPUT_REPOSITORY", "tuanductran/soulmap-ai")
    monkeypatch.setenv("INPUT_BRANCH", "release/prep-1")
    monkeypatch.setenv("INPUT_BASE", "main")
    monkeypatch.delenv("INPUT_TAG", raising=False)
    monkeypatch.delenv("INPUT_BODY", raising=False)
    monkeypatch.delenv("INPUT_BODY_PATH", raising=False)

    with (
        patch.object(
            client,
            "paginated",
            return_value=[{"number": 1}, {"number": 2}],
        ),
        pytest.raises(action.GitHubActionError) as captured,
    ):
        action.run_pull_request(client)
    assert "multiple open release PRs" in str(captured.value)
