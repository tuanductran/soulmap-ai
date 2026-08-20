from __future__ import annotations

from typing import Any, cast
from wsgiref.types import StartResponse

import pytest

from soulmap.web.config import ALPINE_URL, HTMX_URL, INTER_CSS_URL
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
def test_nav_path_keeps_english_unprefixed(route: str, locale: str, expected: str) -> None:
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
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
    assert headers["Cache-Control"] == "no-store"


def test_resource_hints_preconnect_dns_prefetch_and_css_preload_are_deduplicated() -> None:
    hints = resource_hints()

    assert f'<link rel="preconnect" href="{origin(INTER_CSS_URL)}">' in hints
    assert f'<link rel="dns-prefetch" href="{origin(INTER_CSS_URL)}">' in hints
    assert f'<link rel="dns-prefetch" href="{origin(HTMX_URL)}">' in hints
    assert f'<link rel="dns-prefetch" href="{origin(ALPINE_URL)}">' in hints
    assert hints.count('rel="dns-prefetch"') == 2
    assert f'<link rel="preload" href="{INTER_CSS_URL}" as="style" type="text/css">' in hints
