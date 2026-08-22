"""Framework-neutral JSON parsing and mapping validation utilities."""

from __future__ import annotations

import json

JsonValue = dict[str, object] | list[object]


def _checked_raw_json(raw: str, *, max_bytes: int | None) -> str:
    if not raw:
        raise ValueError("No input provided.")

    raw_bytes = raw.encode("utf-8")
    if max_bytes is not None and len(raw_bytes) > max_bytes:
        raise ValueError(
            f"Input too large ({len(raw_bytes)} bytes). Max is {max_bytes} bytes."
        )
    return raw


def parse_json_object(
    raw: str, *, max_bytes: int | None = 200_000
) -> dict[str, object]:
    """Parse JSON and require an object payload."""

    raw = _checked_raw_json(raw, max_bytes=max_bytes)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON parse error: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")
    return payload


def parse_json_value(raw: str, *, max_bytes: int | None = 200_000) -> JsonValue:
    """Parse JSON and allow either an object or list payload."""

    raw = _checked_raw_json(raw, max_bytes=max_bytes)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON parse error: {error}") from error
    if not isinstance(payload, (dict, list)):
        raise ValueError("Input must be a JSON object or array.")
    return payload


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
    """Return a list field or an empty default when omitted."""

    value = payload.get(name, [])
    if not isinstance(value, list):
        raise ValueError(f"Field '{name}' must be a list.")
    return value


def require_dict_field(payload: dict[str, object], name: str) -> dict[str, object]:
    """Return a dictionary field or an empty default when omitted."""

    value = payload.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"Field '{name}' must be a JSON object.")
    return value
