"""SoulMap CLI compatibility boundary for JSON payload handling.

Generic JSON parsing and field validation live in :mod:`soulmate.data.json`.
This module retains SoulMap's environment, stdin, error-shape, and
message-history conventions.
"""

from __future__ import annotations

import json
import os
import sys

from soulmate.data.json import (
    JsonValue,
    require_dict_field,
    require_list_field,
    require_non_empty_str_field,
    require_str_field,
)
from soulmate.data.json import (
    parse_json_object as _parse_json_object,
)
from soulmate.data.json import (
    parse_json_value as _parse_json_value,
)

__all__ = [
    "JsonValue",
    "parse_json_object",
    "parse_json_value",
    "print_json_error",
    "read_stdin_json",
    "read_stdin_json_value",
    "require_dict_field",
    "require_list_field",
    "require_message_history_fields",
    "require_message_history_memory_fields",
    "require_message_history_memory_selection_fields",
    "require_non_empty_str_field",
    "require_str_field",
]


def _max_input_bytes() -> int:
    max_bytes_env = os.getenv("SOULMAP_MAX_INPUT_BYTES", "").strip()
    if not max_bytes_env:
        return 200_000
    try:
        return int(max_bytes_env)
    except ValueError:
        raise ValueError("SOULMAP_MAX_INPUT_BYTES must be an integer.") from None


def _checked_raw_json(raw: str) -> str:
    """Validate SoulMap's environment-based stdin byte limit."""

    max_bytes = _max_input_bytes()
    if not raw:
        raise ValueError("No input provided.")
    raw_bytes = raw.encode("utf-8")
    if len(raw_bytes) > max_bytes:
        raise ValueError(
            f"Input too large ({len(raw_bytes)} bytes). Max is {max_bytes} bytes."
        )
    return raw


def parse_json_object(raw: str) -> dict[str, object]:
    """Parse a SoulMap JSON object using the generic foundation parser."""

    return _parse_json_object(_checked_raw_json(raw), max_bytes=None)


def parse_json_value(raw: str) -> JsonValue:
    """Parse a SoulMap object-or-array using the generic foundation parser."""

    return _parse_json_value(_checked_raw_json(raw), max_bytes=None)


def read_stdin_json(*, strip: bool = False) -> dict[str, object]:
    """Read stdin and parse it as a JSON object payload."""

    raw = sys.stdin.read()
    return parse_json_object(raw.strip() if strip else raw)


def read_stdin_json_value(*, strip: bool = False) -> JsonValue:
    """Read stdin and parse it as a JSON object-or-array payload."""

    raw = sys.stdin.read()
    return parse_json_value(raw.strip() if strip else raw)


def print_json_error(error: Exception | str, *, ensure_ascii: bool = False) -> None:
    """Print a JSON error payload using SoulMap's standard shape."""

    message = error if isinstance(error, str) else str(error)
    print(json.dumps({"error": message}, ensure_ascii=ensure_ascii))


def require_message_history_fields(
    payload: dict[str, object],
) -> tuple[str, list[dict[str, str]]]:
    """Return the common SoulMap message/history detector payload."""

    return require_non_empty_str_field(payload, "message"), require_list_field(
        payload, "history"
    )


def require_message_history_memory_fields(
    payload: dict[str, object],
) -> tuple[str, list[dict[str, str]], dict[str, object]]:
    """Return the common SoulMap message/history/memory payload."""

    message, history = require_message_history_fields(payload)
    return message, history, require_dict_field(payload, "memory")


def require_message_history_memory_selection_fields(
    payload: dict[str, object],
) -> tuple[str, list[dict[str, str]], dict[str, object], dict[str, object]]:
    """Return the common SoulMap message/history/memory/selection payload."""

    message, history, memory = require_message_history_memory_fields(payload)
    return message, history, memory, require_dict_field(payload, "selection")
