from __future__ import annotations

from typing import Any, cast
from wsgiref.types import StartResponse

import pytest

from soulmap.web.config import ALPINE_URL, HTMX_URL
from soulmap.web.http import (
    nav_path,
    normalise_request_path,
    origin,
    resource_hints,
    response,
    text,
)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.com/path", "https://example.com/"),
        ("http://localhost:8814/", "http://localhost:8814/"),
        ("javascript:alert(1)", None),
        ("/relative/path", None),
        ("https:///missing-host", None),
        ("", None),
    ],
)
def test_origin_accepts_only_http_urls(url: str, expected: str | None) -> None:
    assert origin(url) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/", ("/", "en")),
        ("", ("/", "en")),
        ("/how-it-works", ("/how-it-works", "en")),
        ("/vi/how-it-works", ("/how-it-works", "vi")),
        ("/ko/faq/", ("/faq", "ko")),
        ("///vi///privacy///", ("///privacy", "vi")),
        ("/fr/faq", ("/fr/faq", "en")),
    ],
)
def test_normalise_request_path_handles_supported_locale_prefixes(
    path: str, expected: tuple[str, str]
) -> None:
    assert normalise_request_path(path) == expected


@pytest.mark.parametrize(
    ("route", "locale", "expected"),
    [
        ("/", "en", "/"),
        ("/faq", "en", "/faq"),
        ("/", "vi", "/vi"),
        ("/faq", "vi", "/vi/faq"),
        ("/privacy", "ko", "/ko/privacy"),
    ],
)
def test_nav_path_keeps_english_unprefixed(
    route: str, locale: str, expected: str
) -> None:
    assert nav_path(route, locale) == expected


def test_text_escapes_localized_values_and_unknown_keys_are_stable() -> None:
    assert text("en", "brand_home_label") == "SoulMap AI home"
    assert text("vi", "missing_key") == "missing_key"


def test_response_has_shared_security_headers_and_byte_length() -> None:
    captured: dict[str, Any] = {}

    def capture(
        status: str, headers: list[tuple[str, str]], *_args: object
    ) -> StartResponse:
        captured["status"] = status
        captured["headers"] = headers
        return cast(StartResponse, lambda _body: None)

    body = response(
        cast(StartResponse, capture),
        "200 OK",
        "text/plain",
        "hé",
        [("Cache-Control", "no-store")],
    )
    headers = dict(cast(list[tuple[str, str]], captured["headers"]))
    assert captured["status"] == "200 OK"
    assert body == ["hé".encode()]
    assert headers["Content-Length"] == str(len(body[0]))
    assert headers["X-Content-Type-Options"] == "nosniff"
    csp = headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in csp
    assert "style-src 'self'" in csp
    assert "style-src-attr 'unsafe-inline'" in csp
    assert "font-src 'self'" in csp
    assert "rsms.me" not in csp
    assert headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
    assert headers["Cache-Control"] == "no-store"


def test_resource_hints_skips_preconnect_when_critical_origin_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("soulmap.web.http.HTMX_URL", "javascript:alert(1)")
    monkeypatch.setattr("soulmap.web.http.ALPINE_URL", "https://cdn.example/alpine.js")

    hints = resource_hints()

    assert 'rel="preconnect"' not in hints
    assert '<link rel="dns-prefetch" href="https://cdn.example/">' in hints


def test_resource_hints_preconnect_and_dns_prefetch_are_deduplicated() -> None:
    hints = resource_hints()

    assert f'<link rel="preconnect" href="{origin(HTMX_URL)}">' in hints
    assert f'<link rel="dns-prefetch" href="{origin(HTMX_URL)}">' in hints
    assert f'<link rel="dns-prefetch" href="{origin(ALPINE_URL)}">' in hints
    assert hints.count('rel="dns-prefetch"') == 1
    assert 'rel="preload"' not in hints
    assert "rsms.me/inter" not in hints
