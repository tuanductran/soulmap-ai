"""Helpers for validating JSON CLI payloads."""

from __future__ import annotations

import json
import os
import sys

JsonValue = dict[str, object] | list[object]


def _checked_raw_json(raw: str) -> str:
    """Validate raw stdin size and environment-based byte limits."""
    if not raw:
        raise ValueError("No input provided.")

    max_bytes_env = os.getenv("SOULMAP_MAX_INPUT_BYTES", "").strip()
    max_bytes = 200_000
    if max_bytes_env:
        try:
            max_bytes = int(max_bytes_env)
        except ValueError:
            raise ValueError("SOULMAP_MAX_INPUT_BYTES must be an integer.") from None

    raw_bytes = raw.encode("utf-8")
    if len(raw_bytes) > max_bytes:
        raise ValueError(
            f"Input too large ({len(raw_bytes)} bytes). Max is {max_bytes} bytes."
        )

    return raw


def parse_json_object(raw: str) -> dict[str, object]:
    """Parse stdin JSON and require an object payload."""
    raw = _checked_raw_json(raw)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON parse error: {error}") from error

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")

    return payload


def parse_json_value(raw: str) -> JsonValue:
    """Parse stdin JSON and allow either object or list payloads."""
    raw = _checked_raw_json(raw)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON parse error: {error}") from error

    if not isinstance(payload, (dict, list)):
        raise ValueError("Input must be a JSON object or array.")

    return payload


def read_stdin_json(*, strip: bool = False) -> dict[str, object]:
    """Read stdin and parse it as a JSON object payload."""
    raw = sys.stdin.read()
    return parse_json_object(raw.strip() if strip else raw)


def read_stdin_json_value(*, strip: bool = False) -> JsonValue:
    """Read stdin and parse it as a JSON object-or-array payload."""
    raw = sys.stdin.read()
    return parse_json_value(raw.strip() if strip else raw)


def print_json_error(error: Exception | str, *, ensure_ascii: bool = False) -> None:
    """Print a JSON error payload using the repo's standard shape."""
    message = error if isinstance(error, str) else str(error)
    print(json.dumps({"error": message}, ensure_ascii=ensure_ascii))


def require_str_field(payload: dict[str, object], name: str) -> str:
    """Return a string field or an empty default when omitted."""
    value = payload.get(name, "")
    if not isinstance(value, str):
        raise ValueError(f"Field '{name}' must be a string.")
    return value


def require_non_empty_str_field(payload: dict[str, object], name: str) -> str:
    """Return a required non-empty string field."""
    value = require_str_field(payload, name)
    if not value:
        raise ValueError(f"No '{name}' field in input.")
    return value


def require_list_field(payload: dict[str, object], name: str) -> list[dict[str, str]]:
    """Return a message-list field or an empty default when omitted.

    Every item is normalized to a dict with string "role" and "content" keys.
    A non-dict item is dropped, and a missing or non-string "role"/"content"
    on a dict item is coerced to "". Every detector indexes history items as
    ``m["content"]`` without a fallback, so this guarantees that never raises
    a KeyError on a malformed history entry (a truncated or partial message
    record) instead of crashing the whole request.
    """
    value = payload.get(name, [])
    if not isinstance(value, list):
        raise ValueError(f"Field '{name}' must be a list.")

    normalized: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        role = item.get("role", "")
        content = item.get("content", "")
        normalized.append(
            {
                "role": role if isinstance(role, str) else "",
                "content": content if isinstance(content, str) else "",
            }
        )
    return normalized


def require_dict_field(payload: dict[str, object], name: str) -> dict[str, object]:
    """Return a dict field or an empty default when omitted."""
    value = payload.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"Field '{name}' must be a JSON object.")
    return value


def require_message_history_fields(
    payload: dict[str, object],
) -> tuple[str, list[dict[str, str]]]:
    """Return the common message/history detector payload."""
    return require_non_empty_str_field(payload, "message"), require_list_field(
        payload, "history"
    )


def require_message_history_memory_fields(
    payload: dict[str, object],
) -> tuple[str, list[dict[str, str]], dict[str, object]]:
    """Return the common message/history/memory payload."""
    message, history = require_message_history_fields(payload)
    return message, history, require_dict_field(payload, "memory")


def require_message_history_memory_selection_fields(
    payload: dict[str, object],
) -> tuple[str, list[dict[str, str]], dict[str, object], dict[str, object]]:
    """Return the common message/history/memory/selection payload."""
    message, history, memory = require_message_history_memory_fields(payload)
    return message, history, memory, require_dict_field(payload, "selection")
