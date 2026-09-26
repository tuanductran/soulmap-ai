from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from urllib.error import HTTPError


ROOT = Path(__file__).parents[2]
ACTION_PATH = ROOT / "src" / "action" / "__main__.py"

_spec = importlib.util.spec_from_file_location("soulmap_action", ACTION_PATH)
assert _spec is not None
assert _spec.loader is not None
action = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(action)


class FakeResponse:
    def __init__(self, payload: object, headers: dict[str, str] | None = None) -> None:
        self.status = 200
        self.headers = headers or {}
        self._payload = json.dumps(payload).encode()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

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
    error = HTTPError(
        "https://api.github.com/repos/a/b",
        403,
        "Forbidden",
        {"X-RateLimit-Remaining": "0"},
        io.BytesIO(json.dumps({"message": f"token={token}"}).encode()),
    )
    client = action.GitHubClient(token)

    with patch.object(action, "urlopen", side_effect=error):
        try:
            client.api("GET", "/repos/a/b")
        except action.GitHubAPIError as exc:
            assert exc.status == 403
            assert token not in str(exc)
            assert "[REDACTED]" in exc.detail
        else:
            raise AssertionError("expected GitHubAPIError")


def test_transient_http_error_is_retried() -> None:
    error = HTTPError(
        "https://api.github.com/repos/a/b",
        503,
        "Unavailable",
        {},
        __import__("io").BytesIO(b'{"message":"try again"}'),
    )
    calls = iter([error, FakeResponse({"ok": True})])
    client = action.GitHubClient("token")

    with patch.object(
        action, "urlopen", side_effect=lambda _request: next(calls)
    ):
        with patch.object(action.time, "sleep") as sleep:
            assert client.api("GET", "/repos/a/b") == {"ok": True}
            assert sleep.call_count == 1


def test_paginated_requests_continue_until_short_page() -> None:
    client = action.GitHubClient("token")
    responses = iter([[{"number": 1}, {"number": 2}], [{"number": 3}]])

    with patch.object(
        client, "api", side_effect=lambda *_args, **_kwargs: next(responses)
    ):
        assert client.paginated("/repos/a/b/pulls", params={"state": "open"}) == [
            {"number": 1},
            {"number": 2},
            {"number": 3},
        ]


def test_asset_upload_requires_github_confirmation(tmp_path: Path) -> None:
    asset = tmp_path / "artifact.zip"
    asset.write_bytes(b"artifact")
    client = action.GitHubClient("token")
    release = {
        "upload_url": "https://uploads.github.com/repos/a/b/releases/1/assets{?name,label}",
        "assets": [],
    }

    with patch.object(client, "upload", return_value={"name": "other.zip"}):
        try:
            action.upload_assets(client, release, [asset])
        except action.GitHubActionError as exc:
            assert "artifact.zip" in str(exc)
        else:
            raise AssertionError("expected upload confirmation failure")


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

    try:
        action.upload_assets(client, release, [asset])
    except action.GitHubActionError as exc:
        assert "digest does not match" in str(exc)
    else:
        raise AssertionError("expected asset digest mismatch")


def test_existing_asset_with_different_size_is_rejected(tmp_path: Path) -> None:
    asset = tmp_path / "artifact.zip"
    asset.write_bytes(b"new")
    client = action.GitHubClient("token")
    release = {
        "upload_url": "https://uploads.github.com/repos/a/b/releases/1/assets{?name,label}",
        "assets": [{"name": "artifact.zip", "size": 99, "state": "uploaded"}],
    }

    try:
        action.upload_assets(client, release, [asset])
    except action.GitHubActionError as exc:
        assert "refusing to silently publish" in str(exc)
    else:
        raise AssertionError("expected asset size mismatch")


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

    with patch.object(
        client,
        "paginated",
        return_value=[{"number": 1}, {"number": 2}],
    ):
        try:
            action.run_pull_request(client)
        except action.GitHubActionError as exc:
            assert "multiple open release PRs" in str(exc)
        else:
            raise AssertionError("expected duplicate PR protection")
