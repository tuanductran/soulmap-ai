from __future__ import annotations

import io

import pytest

from soulmap_runtime.io.cli_payload import (
    parse_json_object,
    parse_json_value,
    print_json_error,
    read_stdin_json,
    read_stdin_json_value,
    require_message_history_fields,
    require_message_history_memory_fields,
    require_message_history_memory_selection_fields,
    require_non_empty_str_field,
)


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


def test_read_stdin_json_strips_before_parsing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO('  {"a": 1}  '))
    assert read_stdin_json(strip=True) == {"a": 1}


def test_print_json_error_uses_standard_error_shape(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_json_error(ValueError("bad input"))
    captured = capsys.readouterr()
    assert captured.out.strip() == '{"error": "bad input"}'


def test_parse_json_value_accepts_array_payload() -> None:
    assert parse_json_value('[{"role": "user", "content": "hi"}]') == [
        {"role": "user", "content": "hi"}
    ]


def test_read_stdin_json_value_accepts_array_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(' [{"role": "user"}] '))
    assert read_stdin_json_value(strip=True) == [{"role": "user"}]


def test_require_non_empty_str_field_rejects_blank_value() -> None:
    with pytest.raises(ValueError, match=r"No 'message' field in input."):
        require_non_empty_str_field({"message": ""}, "message")


def test_require_message_history_fields_returns_common_detector_payload() -> None:
    payload = {
        "message": "hello",
        "history": [{"role": "user", "content": "hello"}],
    }
    assert require_message_history_fields(payload) == (
        "hello",
        [{"role": "user", "content": "hello"}],
    )


def test_require_message_history_memory_fields_returns_common_selector_payload() -> (
    None
):
    payload = {
        "message": "hello",
        "history": [{"role": "user", "content": "hello"}],
        "memory": {"stage": 1},
    }
    assert require_message_history_memory_fields(payload) == (
        "hello",
        [{"role": "user", "content": "hello"}],
        {"stage": 1},
    )


def test_require_message_history_memory_selection_fields_returns_gate_payload() -> None:
    payload = {
        "message": "hello",
        "history": [{"role": "user", "content": "hello"}],
        "memory": {"stage": 1},
        "selection": {"primary_framework": "MIRROR"},
    }
    assert require_message_history_memory_selection_fields(payload) == (
        "hello",
        [{"role": "user", "content": "hello"}],
        {"stage": 1},
        {"primary_framework": "MIRROR"},
    )
