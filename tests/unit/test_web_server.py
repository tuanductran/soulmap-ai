from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from wsgiref.types import StartResponse
from wsgiref.util import setup_testing_defaults

import pytest

from soulmap.cli import _command_table
from soulmap.web.server import application, export_static


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
    assert "--gold: #8a681f" in css
    assert "--muted: #5d6b70" in css
    assert "--radius-hero: 32px" in css
    assert "--radius-hero-inner: 20px" in css
    assert "border-radius: var(--radius-hero) 36px 28px 32px" in css
    assert "border-radius: 40% 40% 34% 34% / 34% 34% 42% 42%" not in css
    assert "#c99b50" not in css
    assert "prefers-reduced-motion" in css
    assert "prefers-color-scheme: dark" in css
    assert "prefers-reduced-transparency" in css
    assert "safe-area-inset" in css
    assert ":focus-visible" in css
    assert "min-height: 44px" in css
    assert ".skip-link" in css


def test_web_command_is_public_cli_surface() -> None:
    assert "web" in _command_table()


def test_secondary_page_card_headings_are_sequential() -> None:
    for path in ("/how-it-works", "/boundaries", "/download", "/notes"):
        _, body = _request(path)
        html = body.decode("utf-8")
        assert html.count("<h1>") == 1
        assert "<h3>" not in html
        assert "<h2" in html


def test_static_export_writes_pages_project_layout(tmp_path: Path) -> None:
    output = tmp_path / "site"
    written = export_static(output, "/soulmap-ai")

    assert len(written) == 8
    assert (output / "index.html").exists()
    assert (output / "how-it-works" / "index.html").exists()
    assert (output / "static" / "site.css").exists()
    assert (output / "robots.txt").exists()

    html = (output / "index.html").read_text(encoding="utf-8")
    assert 'href="/soulmap-ai/' in html
    assert 'href="/"' not in html
    assert "viewport-fit=cover" in html
    assert 'media="(prefers-color-scheme: dark)"' in html
    assert "<script" not in html
