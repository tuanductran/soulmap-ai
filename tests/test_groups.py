"""Validate GROUPS dataset used by the local test harness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parent.parent
GROUPS_PATH = ROOT / "evals" / "groups.json"


class GroupItem(TypedDict):
    t: str
    note: str


class GroupEntry(TypedDict):
    g: str
    cat: str
    items: list[GroupItem]


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
    assert len(fw_groups) == 16, (
        f"Expected 16 framework groups but got {len(fw_groups)}"
    )
