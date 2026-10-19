from __future__ import annotations

import json
import re
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


def test_synthesis_threshold_labels_resolve_only_through_config() -> None:
    """Every threshold display label must have an explicit runtime-key mapping."""
    synthesis_path = REPO_ROOT / "skills" / "frameworks" / "conversation-synthesis.md"
    config = json.loads(
        default_skill_path("config/runtime-keys.json").read_text(encoding="utf-8")
    )
    threshold_rows = load_table_rows(synthesis_path, "Detection thresholds")
    labels = {row[0] for row in threshold_rows}
    mappings = config["synthesis_threshold_keys"]

    assert labels == set(mappings)
    assert set(mappings.values()) == {
        "minimum_user_messages",
        "automatic_synthesis_user_messages",
        "minimum_distinct_recurring_themes_for_automatic_synthesis",
        "maximum_themes_returned",
        "maximum_anchors_per_theme",
        "maximum_longitudinal_themes",
    }


def test_scope_pack_labels_resolve_only_through_config() -> None:
    """Scope pack headings are human-readable labels, not Python-owned keys."""
    from soulmap.runtime.knowledge.scope_source import _contract_body

    scope_path = REPO_ROOT / "skills" / "safety" / "whitelist-blacklist-system.md"
    scope_text = scope_path.read_text(encoding="utf-8")
    body = _contract_body(scope_text)
    config = json.loads(
        default_skill_path("config/runtime-keys.json").read_text(encoding="utf-8")
    )
    pack_keys = config["scope_pack_keys"]

    labels = set(re.findall(r"^### (?P<pack>.+?)\s*$", body, re.MULTILINE))
    assert labels == set(pack_keys)
    assert set(pack_keys.values()) == {
        "WHITELIST_TIER1",
        "WHITELIST_TIER2",
        "BLACKLIST_LAYER1",
        "BLACKLIST_PROHIBITED",
    }
