import pytest

from modules.cli_payload import parse_json_object


def test_parse_json_object_rejects_oversize_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SOULMAP_MAX_INPUT_BYTES", "20")
    # 21 bytes: {"a":"xxxxxxxxxx"} -> 1+? keep it deterministic by building raw bytes.
    raw = '{"a":"' + ("x" * 30) + '"}'
    with pytest.raises(ValueError, match=r"Input too large"):
        parse_json_object(raw)


def test_parse_json_object_rejects_non_integer_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SOULMAP_MAX_INPUT_BYTES", "not-an-int")
    with pytest.raises(ValueError, match=r"SOULMAP_MAX_INPUT_BYTES must be an integer"):
        parse_json_object('{"a": 1}')


def test_parse_json_object_accepts_when_under_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SOULMAP_MAX_INPUT_BYTES", "1000")
    assert parse_json_object('{"a": 1}') == {"a": 1}
