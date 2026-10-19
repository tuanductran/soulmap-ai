from __future__ import annotations

import json
from pathlib import Path

from soulmap.runtime.knowledge.keyword_lists import (
    default_skill_path,
    load_key_value_table,
    load_table_rows,
)
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_key_config_maps_human_labels_to_python_identifiers() -> None:
    anger = load_key_value_table(runtime_skill_path("anger-companion"), "Guidance")
    direction = load_key_value_table(runtime_skill_path("life-direction"), "Scoring")
    inner_parts = load_key_value_table(runtime_skill_path("inner-parts"), "Guidance")

    assert "self_anger" in anger
    assert "Meaning void" not in direction
    assert "meaning_void" in direction
    assert "not_detected" in inner_parts


def test_every_configured_markdown_key_label_resolves_without_raw_keys() -> None:
    """Every declared label must map to a runtime key absent from the Markdown table."""
    config = json.loads(
        default_skill_path("config/runtime-keys.json").read_text(encoding="utf-8")
    )
    for relative_path, tables in config["markdown_key_labels"].items():
        markdown_path = REPO_ROOT / relative_path
        for heading, label_map in tables.items():
            raw_labels = {
                row[0].strip()
                for row in load_table_rows(markdown_path, heading)
                if row and row[0].strip()
            }
            loaded = load_key_value_table(markdown_path, heading)
            for label, runtime_key in label_map.items():
                assert runtime_key in loaded, (
                    f"{relative_path} / {heading}: label {label!r} "
                    f"did not resolve to {runtime_key!r}"
                )
                assert runtime_key not in raw_labels, (
                    f"{relative_path} / {heading}: runtime key {runtime_key!r} "
                    "still appears as a Markdown row label"
                )
