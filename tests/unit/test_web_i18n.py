from __future__ import annotations

import json

import pytest

from soulmap.web.i18n import LOCALES, SUPPORTED_LOCALES, messages_for, messages_json


def test_json_catalogs_are_loaded_for_every_supported_locale() -> None:
    assert set(LOCALES) == set(SUPPORTED_LOCALES) == {"en", "vi", "ko"}
    assert all(LOCALES[locale] for locale in SUPPORTED_LOCALES)


def test_json_catalogs_have_exact_key_parity_with_english() -> None:
    english_keys = set(LOCALES["en"])

    assert all(set(LOCALES[locale]) == english_keys for locale in SUPPORTED_LOCALES)
    assert len(english_keys) >= 190


def test_messages_for_preserves_english_fallback_contract() -> None:
    assert messages_for("vi")["home_h1"] == "Nghe mình rõ hơn."
    assert messages_for("ko")["home_h1"] == "자신의 목소리를 더 분명히 들으세요."
    assert messages_for("fr") is LOCALES["en"]


def test_messages_json_is_valid_unicode_json_and_escapes_markup_delimiters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(LOCALES["en"], "__test_markup", "<script>&</script>")
    payload = messages_json("en")

    assert "<script>" not in payload
    assert "&" not in payload
    decoded = json.loads(payload)
    assert decoded["__test_markup"] == "<script>&</script>"


def test_unknown_locale_json_uses_english_catalog() -> None:
    assert messages_json("unknown") == messages_json("en")
