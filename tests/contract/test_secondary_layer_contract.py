"""The documented secondary layers must match what the selector can emit.

`skills/meta/orchestration.md` publishes a secondary-layer table that readers
and AI tools treat as the complete set. Nothing tied it to the runtime, so
`inner_parts` was emittable for some time without appearing there.

This reads the table and the selector's own source rather than restating either,
so adding a layer in one place and forgetting the other fails here.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from soulmap.runtime.knowledge.orchestration_source import load_orchestration_rules

REPO_ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATION = REPO_ROOT / "skills" / "meta" / "orchestration.md"
RUNTIME_KEYS = REPO_ROOT / "config" / "runtime-keys.json"
SELECTOR = (
    REPO_ROOT / "src" / "soulmap" / "runtime" / "routing" / "framework_selector.py"
)


def _documented_layers() -> set[str]:
    """Read the secondary-layer table from the doctrine file."""
    text = ORCHESTRATION.read_text(encoding="utf-8")
    section = text.split("| Secondary Layer | Activate When |", 1)[1]
    section = section.split("\nDo NOT activate", 1)[0]
    labels = [
        label.strip().strip("`")
        for label in re.findall(r"^\| ([^|]+) \|", section, re.MULTILINE)
    ]
    aliases = json.loads(RUNTIME_KEYS.read_text(encoding="utf-8"))[
        "orchestration_value_keys"
    ]
    return {aliases.get(label, label.lower()).lower() for label in labels}


def _resulting_strings(node: ast.expr) -> set[str]:
    """Return the strings an expression can evaluate to.

    Only the result matters. A string inside a condition, such as the key in
    `insight.get("insight_detected")`, is not a value the field can take.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.IfExp):
        return _resulting_strings(node.body) | _resulting_strings(node.orelse)
    return set()


def _emittable_layers() -> set[str]:
    """Collect every literal the selector can assign to secondary_layer."""
    tree = ast.parse(SELECTOR.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=True):
                if isinstance(key, ast.Constant) and key.value == "secondary_layer":
                    found |= _resulting_strings(value)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "secondary":
                    found |= _resulting_strings(node.value)
    return found


def test_every_emittable_secondary_layer_is_documented() -> None:
    """A layer the runtime can emit must appear in the doctrine table.

    An undocumented layer reaches the response with no published meaning, so a
    reader of the shipped package cannot tell what it asks for.
    """
    undocumented = _emittable_layers() - _documented_layers()

    assert not undocumented, (
        f"secondary layers emitted but missing from orchestration.md: "
        f"{sorted(undocumented)}"
    )


def test_every_documented_secondary_layer_is_reachable() -> None:
    """A documented layer the runtime never emits is a promise it cannot keep."""
    unreachable = _documented_layers() - _emittable_layers()

    assert not unreachable, (
        f"secondary layers documented but never emitted: {sorted(unreachable)}"
    )

def test_intensity_fallback_secondary_layers_use_runtime_identifiers() -> None:
    """Display labels in Markdown must normalize to selector-facing layer IDs."""
    rules = load_orchestration_rules()

    assert all(
        layer == layer.lower()
        for fallback in rules.intensity_fallback
        for layer in fallback.allowed_secondary
    )
    moderate = next(
        fallback for fallback in rules.intensity_fallback if fallback.level == "MODERATE"
    )
    assert set(moderate.allowed_secondary) == {"meaning_integration", "inner_parts"}
