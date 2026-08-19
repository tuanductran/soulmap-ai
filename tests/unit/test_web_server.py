from collections.abc import Callable
from typing import Any, cast
from wsgiref.types import StartResponse
from wsgiref.util import setup_testing_defaults

import pytest

from soulmap.cli import _command_table
from soulmap.web.server import application


def _request(path: str) -> tuple[dict[str, Any], bytes]:
    environ: dict[str, Any] = {}
    setup_testing_defaults(environ)
    environ["PATH_INFO"] = path
    captured: dict[str, Any] = {}

    def capture(
        status: str,
        headers: list[tuple[str, str]],
        *_args: object,
    ) -> Callable[[bytes], object]:
        captured["status"] = status
        captured["headers"] = headers
        return lambda _body: None

    body = b"".join(application(environ, cast(StartResponse, capture)))
    return captured, body


@pytest.mark.parametrize(
    ("path", "status"),
    [
        ("/", "200 OK"),
        ("/how-it-works", "200 OK"),
        ("/boundaries", "200 OK"),
        ("/download", "200 OK"),
        ("/notes", "200 OK"),
        ("/about", "200 OK"),
        ("/static/site.css", "200 OK"),
        ("/missing", "404 Not Found"),
    ],
)
def test_public_website_routes(path: str, status: str) -> None:
    captured, body = _request(path)

    assert captured["status"] == status
    assert body
    headers = dict(cast(list[tuple[str, str]], captured["headers"]))
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


def test_website_is_responsive_and_accessible() -> None:
    captured, body = _request("/static/site.css")

    assert captured["status"] == "200 OK"
    css = body.decode("utf-8")
    assert "@media (max-width: 640px)" in css
    assert "prefers-reduced-motion" in css
    assert ".skip-link" in css


def test_web_command_is_public_cli_surface() -> None:
    assert "web" in _command_table()
