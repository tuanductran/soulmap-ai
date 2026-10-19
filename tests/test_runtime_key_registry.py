from __future__ import annotations

from soulmap.runtime.knowledge.keyword_lists import load_key_value_table
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path


def test_runtime_key_config_maps_human_labels_to_python_identifiers() -> None:
    anger = load_key_value_table(runtime_skill_path("anger-companion"), "Guidance")
    direction = load_key_value_table(runtime_skill_path("life-direction"), "Scoring")
    inner_parts = load_key_value_table(runtime_skill_path("inner-parts"), "Guidance")

    assert "self_anger" in anger
    assert "Meaning void" not in direction
    assert "meaning_void" in direction
    assert "not_detected" in inner_parts
