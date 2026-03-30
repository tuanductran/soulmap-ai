from __future__ import annotations

import json

from hypothesis import given
from hypothesis import strategies as st

from soulmap_runtime.io.cli_payload import parse_json_object, parse_json_value
from soulmap_runtime.io.text_normalization import normalize_message_text

json_text_strategy = st.text(max_size=32)
json_scalar_strategy = st.none() | st.booleans() | st.integers() | json_text_strategy
json_value_strategy = st.recursive(
    json_scalar_strategy,
    lambda children: (
        st.lists(children, max_size=3)
        | st.dictionaries(json_text_strategy, children, max_size=3)
    ),
    max_leaves=6,
)
json_object_strategy = st.dictionaries(
    json_text_strategy, json_value_strategy, max_size=3
)


@given(st.text())
def test_normalize_message_text_is_lowercase_and_collapses_whitespace(
    message: str,
) -> None:
    normalized = normalize_message_text(message)

    assert normalized == normalized.lower()
    assert "\u2019" not in normalized
    assert "`" not in normalized
    assert normalized == normalized.strip()
    assert "\n" not in normalized
    assert "\t" not in normalized
    assert "  " not in normalized


@given(json_object_strategy)
def test_parse_json_object_round_trips_json_objects(payload: dict[str, object]) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert parse_json_object(raw) == payload


@given(st.one_of(json_object_strategy, st.lists(json_value_strategy, max_size=5)))
def test_parse_json_value_round_trips_json_values(
    payload: dict[str, object] | list[object],
) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert parse_json_value(raw) == payload
