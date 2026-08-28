"""Routing-group evaluation runner.

Runs every case in ``evals/datasets/groups.json`` through the framework
selector and the scope classifier, and compares the result against the
case's expectations. This is a deterministic regression gate: it checks which
framework a message routes to, never the quality of any response text.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from typing import NotRequired, TypedDict

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.routing.framework_selector import select_framework
from soulmap.runtime.routing.scope_classifier import classify_message


class GroupItem(TypedDict):
    """One routing case and what it must produce.

    Every expectation is optional, so a case asserts only what it is about.

    Attributes:
        t: The message text to route.
        note: What this case is testing, for the failure report.
        expect_primary_framework: The framework the message must route to.
        expect_secondary_layer: The annotated secondary layer, or None when
            the case asserts there is none.
        expect_mode: The response mode the route must select.
        expect_scope_tier: The scope classifier's tier.
        expect_scope_category: The scope classifier's category.
        expect_safety_status: The safety gate's status.
        expect_safety_reason: The safety gate's reason code.
    """

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
    """A named group of routing cases that share a rationale.

    Attributes:
        g: Human-readable group name.
        cat: Short category code used to filter runs.
        items: The cases in this group.
        sources: Knowledge files that justify the group's existence.
        source_markers: Quoted text from those files backing specific cases,
            so a reviewer can trace a case to the doctrine behind it.
    """

    g: str
    cat: str
    items: list[GroupItem]
    sources: NotRequired[list[str]]
    source_markers: NotRequired[dict[str, str | list[str]]]


def _load_groups() -> list[GroupEntry]:
    path = REPO_ROOT / "evals" / "datasets" / "groups.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_sources(
    source_paths: list[str],
    source_markers: dict[str, str | list[str]] | None = None,
) -> tuple[list[dict[str, object]], int, int]:
    details: list[dict[str, object]] = []
    failures = 0
    marker_checks = 0
    source_markers = source_markers or {}

    for rel_path in source_paths:
        path = REPO_ROOT / rel_path
        exists = path.exists()
        chars = path.stat().st_size if exists else 0
        ok = exists and chars > 0
        markers = source_markers.get(rel_path)
        matched_markers: list[str] = []
        marker_ok = True

        if markers is not None:
            marker_checks += 1
            marker_values = [markers] if isinstance(markers, str) else list(markers)
            text = path.read_text(encoding="utf-8") if exists else ""
            matched_markers = [marker for marker in marker_values if marker in text]
            marker_ok = bool(matched_markers)

        if not ok or not marker_ok:
            failures += 1
        details.append(
            {
                "path": rel_path,
                "exists": exists,
                "chars": chars,
                "markers": (
                    [markers] if isinstance(markers, str) else list(markers or [])
                ),
                "matched_markers": matched_markers,
                "ok": ok and marker_ok,
            }
        )

    return details, failures, marker_checks


def run_groups_eval(
    *,
    category: str | None = None,
    group_name: str | None = None,
) -> dict[str, object]:
    """Run the routing-group evaluation.

    Args:
        category: Only run groups with this category code, or None for all.
        group_name: Only run the group with this name, or None for all.

    Returns:
        A summary dict carrying the totals, the per-group results, and the
        source-marker checks. A run is clean when ``failed_checks`` is 0.
    """
    groups = _load_groups()
    if category:
        groups = [group for group in groups if group["cat"] == category]
    if group_name:
        groups = [group for group in groups if group["g"] == group_name]

    results: list[dict[str, object]] = []
    assertion_checks = 0
    asserted_items = 0
    failed = 0
    source_checks = 0
    failed_source_checks = 0
    source_marker_checks = 0

    for group in groups:
        source_paths = group.get("sources", [])
        source_details, source_failures, marker_checks = _validate_sources(
            source_paths,
            group.get("source_markers"),
        )
        source_checks += len(source_details)
        failed_source_checks += source_failures
        source_marker_checks += marker_checks

        for item in group["items"]:
            message = item["t"]
            history = [{"role": "user", "content": message}]
            scope = classify_message(message)
            selection = select_framework(
                message,
                history,
                {},
            )
            expected_primary = item.get("expect_primary_framework")
            expected_secondary = item.get("expect_secondary_layer")
            expected_mode = item.get("expect_mode")
            expected_scope_tier = item.get("expect_scope_tier")
            expected_scope_category = item.get("expect_scope_category")
            expected_safety_status = item.get("expect_safety_status")
            expected_safety_reason = item.get("expect_safety_reason")
            item_has_expectation = False

            checks: list[bool] = []
            if expected_primary is not None:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(selection["primary_framework"] == expected_primary)
            if "expect_secondary_layer" in item:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(selection.get("secondary_layer") == expected_secondary)
            if expected_mode is not None:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(selection.get("mode") == expected_mode)
            if expected_scope_tier is not None:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(scope["tier"] == expected_scope_tier)
            if expected_scope_category is not None:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(scope["category"] == expected_scope_category)
            if expected_safety_status is not None:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(selection.get("safety_status") == expected_safety_status)
            if expected_safety_reason is not None:
                assertion_checks += 1
                item_has_expectation = True
                checks.append(selection.get("safety_reason") == expected_safety_reason)

            if item_has_expectation:
                asserted_items += 1

            passed = all(checks) if checks else None
            if passed is False:
                failed += 1

            results.append(
                {
                    "group": group["g"],
                    "category": group["cat"],
                    "message": message,
                    "note": item["note"],
                    "sources": source_details,
                    "expected_primary_framework": expected_primary,
                    "expected_secondary_layer": (
                        expected_secondary if "expect_secondary_layer" in item else None
                    ),
                    "expected_mode": expected_mode,
                    "expected_scope_tier": expected_scope_tier,
                    "expected_scope_category": expected_scope_category,
                    "expected_safety_status": expected_safety_status,
                    "expected_safety_reason": expected_safety_reason,
                    "actual_primary_framework": selection["primary_framework"],
                    "actual_secondary_layer": selection.get("secondary_layer"),
                    "actual_mode": selection.get("mode"),
                    "actual_scope_tier": scope["tier"],
                    "actual_scope_category": scope["category"],
                    "actual_safety_status": selection.get("safety_status"),
                    "actual_safety_reason": selection.get("safety_reason"),
                    "ok": passed,
                }
            )

    summary = {
        "groups": len(groups),
        "items": len(results),
        "asserted_items": asserted_items,
        "unasserted_items": len(results) - asserted_items,
        "assertion_checks": assertion_checks,
        "failed_items": failed,
        "source_checks": source_checks,
        "source_marker_checks": source_marker_checks,
        "failed_source_checks": failed_source_checks,
        "failed_checks": failed + failed_source_checks,
    }

    return {
        "ok": failed == 0 and failed_source_checks == 0,
        "summary": summary,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the routing-group evaluation from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when every check passes, 1 when any case fails.
    """
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Run framework-routing QA checks from evals/datasets/groups.json."
    )
    parser.add_argument("--category", help="Only evaluate one GROUPS category.")
    parser.add_argument("--group", dest="group_name", help="Only evaluate one group.")
    args = parser.parse_args(argv)

    result = run_groups_eval(category=args.category, group_name=args.group_name)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
