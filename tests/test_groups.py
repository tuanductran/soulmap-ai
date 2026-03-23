"""Validate GROUPS dataset used by the local test harness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NotRequired, TypedDict

ROOT = Path(__file__).resolve().parent.parent
GROUPS_PATH = ROOT / "evals" / "groups.json"


class GroupItem(TypedDict):
    t: str
    note: str
    expect_primary_framework: NotRequired[str]
    expect_secondary_layer: NotRequired[str | None]
    expect_mode: NotRequired[str]
    expect_scope_tier: NotRequired[str]
    expect_scope_category: NotRequired[str]
    expect_safety_status: NotRequired[str]
    expect_safety_reason: NotRequired[str]


class GroupEntry(TypedDict):
    g: str
    cat: str
    items: list[GroupItem]
    sources: NotRequired[list[str]]
    source_markers: NotRequired[dict[str, str | list[str]]]


def _load_groups() -> list[GroupEntry]:
    data = json.loads(GROUPS_PATH.read_text(encoding="utf-8"))
    return data


def test_groups_have_expected_categories() -> None:
    groups = _load_groups()
    assert groups, "No GROUPS parsed from evals/groups.json"

    cats = {g["cat"] for g in groups}
    expected = {"fw", "wl1", "wl2", "bl1", "bl2", "red", "edge"}
    assert cats == expected, f"Unexpected GROUPS categories: {cats}"


def test_groups_items_non_empty() -> None:
    groups = _load_groups()
    for group in groups:
        items = group["items"]
        assert items, f"GROUP '{group['g']}' has no items"
        assert all(item["t"].strip() for item in items), (
            f"GROUP '{group['g']}' has empty item text"
        )


def test_framework_group_count_is_expected() -> None:
    groups = _load_groups()
    fw_groups = [g for g in groups if g["cat"] == "fw"]
    assert len(fw_groups) == 23, (
        f"Expected 23 framework groups but got {len(fw_groups)}"
    )


def test_all_groups_define_sources() -> None:
    groups = _load_groups()
    for group in groups:
        assert group.get("sources"), (
            f"GROUP '{group['g']}' has no source file references"
        )


def test_source_markers_only_reference_declared_sources() -> None:
    groups = _load_groups()
    for group in groups:
        sources = set(group.get("sources", []))
        for source_path, markers in group.get("source_markers", {}).items():
            assert source_path in sources, (
                f"GROUP '{group['g']}' defines markers for undeclared source "
                f"'{source_path}'"
            )
            if isinstance(markers, str):
                assert markers.strip(), (
                    f"GROUP '{group['g']}' has an empty marker for '{source_path}'"
                )
            else:
                assert markers, (
                    f"GROUP '{group['g']}' has no markers for '{source_path}'"
                )
                assert all(marker.strip() for marker in markers), (
                    f"GROUP '{group['g']}' has blank markers for '{source_path}'"
                )
