"""JSON-backed localized website copy and safe DOM payload helpers."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Final

SUPPORTED_LOCALES: Final[tuple[str, ...]] = ("en", "vi", "ko")


def _load_locale(locale: str) -> dict[str, str]:
    payload = json.loads(
        files("soulmap.web.locales")
        .joinpath(f"{locale}.json")
        .read_text(encoding="utf-8")
    )
    if not isinstance(payload, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in payload.items()
    ):
        raise ValueError(f"Invalid locale catalog: {locale}")
    return payload


LOCALES: Final[dict[str, dict[str, str]]] = {
    locale: _load_locale(locale) for locale in SUPPORTED_LOCALES
}


def _validate_locale_parity(locales: dict[str, dict[str, str]]) -> None:
    if any(set(messages) != set(locales["en"]) for messages in locales.values()):
        raise ValueError("Locale catalogs must expose the same translation keys")


_validate_locale_parity(LOCALES)


def messages_for(locale: str) -> dict[str, str]:
    """Return the requested locale with English fallback for future additions."""
    return LOCALES.get(locale, LOCALES["en"])


def messages_json(locale: str) -> str:
    """Serialize localized copy for an inert JSON DOM payload."""
    payload = json.dumps(
        messages_for(locale), ensure_ascii=False, separators=(",", ":")
    )
    return (
        payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )
