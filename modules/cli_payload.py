"""Helpers for validating JSON CLI payloads."""

from __future__ import annotations

import json


def parse_json_object(raw: str) -> dict[str, object]:
    """Parse stdin JSON and require an object payload."""
    if not raw:
        raise ValueError("No input provided.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON parse error: {error}") from error

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")

    return payload


def require_str_field(payload: dict[str, object], name: str) -> str:
    """Return a string field or an empty default when omitted."""
    value = payload.get(name, "")
    if not isinstance(value, str):
        raise ValueError(f"Field '{name}' must be a string.")
    return value


def require_list_field(payload: dict[str, object], name: str) -> list[dict[str, str]]:
    """Return a message-list field or an empty default when omitted."""
    value = payload.get(name, [])
    if not isinstance(value, list):
        raise ValueError(f"Field '{name}' must be a list.")
    return value


def require_dict_field(payload: dict[str, object], name: str) -> dict[str, object]:
    """Return a dict field or an empty default when omitted."""
    value = payload.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"Field '{name}' must be a JSON object.")
    return value
