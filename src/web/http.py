"""Pure HTTP and localization helpers for the SoulMap WSGI surface."""

from __future__ import annotations

from html import escape
from urllib.parse import urlparse
from wsgiref.types import StartResponse

from web.config import ALPINE_URL, HTMX_URL
from web.i18n import LOCALES as TEXT
from web.i18n import SUPPORTED_LOCALES


def origin(url: str) -> str | None:
    """Return the scheme/host origin for a valid external URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}/"


def resource_hints() -> str:
    """Generate conservative, deduplicated resource hints from critical URLs."""
    external_urls = (HTMX_URL, ALPINE_URL)
    origins = tuple(
        dict.fromkeys(
            origin_value for url in external_urls if (origin_value := origin(url))
        )
    )
    critical_origin = origin(HTMX_URL)
    hints: list[str] = []
    if critical_origin:
        hints.append(
            f'<link rel="preconnect" href="{escape(critical_origin, quote=True)}">'
        )
    hints.extend(
        f'<link rel="dns-prefetch" href="{escape(value, quote=True)}">'
        for value in origins
    )
    return "\n".join(hints)


def translate(locale: str, key: str) -> str:
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, key))


def nav_path(route: str, locale: str) -> str:
    if locale == "en":
        return route or "/"
    return f"/{locale}{route if route != '/' else ''}"


def text(locale: str, key: str) -> str:
    return escape(translate(locale, key))


def response(
    start_response: StartResponse,
    status: str,
    content_type: str,
    body: str | bytes,
    extra_headers: list[tuple[str, str]] | None = None,
) -> list[bytes]:
    """Build a secure, deterministic WSGI response with shared headers."""
    payload = body if isinstance(body, bytes) else body.encode("utf-8")
    headers = [
        ("Content-Type", f"{content_type}; charset=utf-8"),
        ("Content-Length", str(len(payload))),
        ("X-Content-Type-Options", "nosniff"),
        (
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self'; style-src-attr 'unsafe-inline'; font-src 'self'; "
            "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
            "object-src 'none'",
        ),
        ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status, headers)
    return [payload]


def normalise_request_path(path: str) -> tuple[str, str]:
    """Split an optional supported locale prefix from a request path."""
    normal = "/" + path.strip("/") if path.strip("/") else "/"
    parts = normal.strip("/").split("/") if normal != "/" else []
    if parts and parts[0] in SUPPORTED_LOCALES:
        locale = parts.pop(0)
        route = "/" + "/".join(parts) if parts else "/"
        return route, locale
    return normal, "en"


# Compatibility aliases used by the server facade and characterization tests.
_origin = origin
_resource_hints = resource_hints
tr = translate
_nav_path = nav_path
_text = text
_response = response
_normalise_request_path = normalise_request_path
