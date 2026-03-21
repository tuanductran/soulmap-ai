from __future__ import annotations

from modules.text_normalization import normalize_message_text


def test_normalize_message_text_normalizes_quotes_and_whitespace() -> None:
    assert normalize_message_text("  Don\u2019t   panic`  ") == "don't panic'"


def test_normalize_message_text_can_preserve_outer_whitespace() -> None:
    assert normalize_message_text("  hi\nthere  ", strip=False) == " hi there "
