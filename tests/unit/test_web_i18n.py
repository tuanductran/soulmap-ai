from __future__ import annotations

import json
from importlib.resources import files

import pytest

from soulmap.web.http import translate
from soulmap.web.i18n import LOCALES, SUPPORTED_LOCALES, messages_for, messages_json


def test_json_catalogs_are_loaded_for_every_supported_locale() -> None:
    assert set(LOCALES) == set(SUPPORTED_LOCALES) == {"en", "vi", "ko"}
    assert all(LOCALES[locale] for locale in SUPPORTED_LOCALES)


def test_json_catalog_files_match_loaded_registry_and_have_exact_key_parity() -> None:
    catalogs = {
        locale: json.loads(
            files("soulmap.web.locales")
            .joinpath(f"{locale}.json")
            .read_text(encoding="utf-8")
        )
        for locale in SUPPORTED_LOCALES
    }
    english_keys = set(catalogs["en"])

    assert catalogs == LOCALES
    assert all(set(catalogs[locale]) == english_keys for locale in SUPPORTED_LOCALES)
    assert len(english_keys) == 193


def test_messages_for_preserves_english_fallback_contract() -> None:
    assert messages_for("vi")["home_h1"] == "Nghe mình rõ hơn."
    assert messages_for("ko")["home_h1"] == "자신의 목소리를 더 분명히 들으세요."
    assert messages_for("fr") is LOCALES["en"]


def test_translate_falls_back_to_english_for_a_missing_key_in_a_supported_locale(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(LOCALES["vi"], "home_h1")

    assert translate("vi", "home_h1") == LOCALES["en"]["home_h1"]
    assert translate("vi", "missing_key") == "missing_key"


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
