"""Static asset registry and safe readers for the public web surface."""

from __future__ import annotations

from pathlib import Path

STATIC_DIR = Path(__file__).with_name("static")

_STATIC_ASSETS: dict[str, tuple[str, str]] = {
    "site.css": ("text/css", "utf-8"),
    "site.js": ("text/javascript", "utf-8"),
    "search.js": ("text/javascript", "utf-8"),
}

_FONT_ASSETS: dict[str, tuple[str, str]] = {
    "InterVariable.woff2": ("font/woff2", "binary"),
    "ManropeVariable.woff2": ("font/woff2", "binary"),
}


def read_text_asset(name: str) -> str | None:
    """Read an allow-listed UTF-8 static asset."""
    asset = _STATIC_ASSETS.get(name)
    if asset is None:
        return None
    return (STATIC_DIR / name).read_text(encoding=asset[1])


def read_font_asset(name: str) -> bytes | None:
    """Read an allow-listed local font asset."""
    asset = _FONT_ASSETS.get(name)
    if asset is None:
        return None
    return (STATIC_DIR / "fonts" / name).read_bytes()


def static_asset_type(name: str) -> str | None:
    """Return the content type for an allow-listed asset."""
    if name in _STATIC_ASSETS:
        return _STATIC_ASSETS[name][0]
    if name in _FONT_ASSETS:
        return _FONT_ASSETS[name][0]
    return None
