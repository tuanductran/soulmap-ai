from __future__ import annotations

import io
import json
from pathlib import Path
from typing import cast

import pytest

from soulmap.devtools.evals import eval_groups


def test_validate_sources_reports_markers_and_missing_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "present.md").write_text("required marker\n", encoding="utf-8")
    monkeypatch.setattr(eval_groups, "REPO_ROOT", tmp_path)

    details, failures, marker_checks = eval_groups._validate_sources(
        ["present.md", "missing.md"],
        {"present.md": ["required marker", "not present"], "missing.md": "required"},
    )

    assert failures == 1
    assert marker_checks == 2
    assert details[0]["ok"] is True
    assert details[0]["matched_markers"] == ["required marker"]
    assert details[1]["exists"] is False
    assert details[1]["ok"] is False


def test_run_groups_eval_filters_and_counts_assertions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "source.md").write_text("source marker\n", encoding="utf-8")
    groups = [
        {
            "g": "Keep",
            "cat": "target",
            "sources": ["source.md"],
            "source_markers": {"source.md": "source marker"},
            "items": [
                {
                    "t": "first",
                    "note": "fully asserted",
                    "expect_primary_framework": "MIRROR",
                    "expect_secondary_layer": None,
                    "expect_mode": "MIRROR",
                    "expect_scope_tier": "ALLOW",
                    "expect_scope_category": "inner_work",
                    "expect_safety_status": "PASS",
                    "expect_safety_reason": "no_override",
                },
                {"t": "second", "note": "observational only"},
            ],
        },
        {
            "g": "Skip",
            "cat": "other",
            "items": [{"t": "third", "note": "filtered out"}],
        },
    ]
    selection = {
        "primary_framework": "MIRROR",
        "secondary_layer": None,
        "mode": "MIRROR",
        "safety_status": "PASS",
        "safety_reason": "no_override",
    }

    monkeypatch.setattr(eval_groups, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(eval_groups, "_load_groups", lambda: groups)
    monkeypatch.setattr(
        eval_groups,
        "classify_message",
        lambda _message: {"tier": "ALLOW", "category": "inner_work"},
    )
    monkeypatch.setattr(eval_groups, "select_framework", lambda *_args: selection)

    result = eval_groups.run_groups_eval(category="target", group_name="Keep")

    assert result["ok"] is True
    assert result["summary"] == {
        "groups": 1,
        "items": 2,
        "asserted_items": 1,
        "unasserted_items": 1,
        "assertion_checks": 7,
        "failed_items": 0,
        "source_checks": 1,
        "source_marker_checks": 1,
        "failed_source_checks": 0,
        "failed_checks": 0,
    }
    results = cast(list[dict[str, object]], result["results"])
    assert results[0]["ok"] is True
    assert results[1]["ok"] is None


def test_run_groups_eval_reports_failed_source_and_assertion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    groups = [
        {
            "g": "Broken",
            "cat": "target",
            "sources": ["missing.md"],
            "items": [
                {
                    "t": "message",
                    "note": "wrong expected primary",
                    "expect_primary_framework": "GRIEF",
                }
            ],
        }
    ]

    monkeypatch.setattr(eval_groups, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(eval_groups, "_load_groups", lambda: groups)
    monkeypatch.setattr(
        eval_groups,
        "classify_message",
        lambda _message: {"tier": "ALLOW", "category": "inner_work"},
    )
    monkeypatch.setattr(
        eval_groups,
        "select_framework",
        lambda *_args: {"primary_framework": "MIRROR", "mode": "MIRROR"},
    )

    result = eval_groups.run_groups_eval()

    assert result["ok"] is False
    summary = cast(dict[str, object], result["summary"])
    assert summary["failed_items"] == 1
    assert summary["failed_source_checks"] == 1
    assert summary["failed_checks"] == 2
    results = cast(list[dict[str, object]], result["results"])
    assert results[0]["ok"] is False


def test_run_groups_eval_returns_empty_summary_for_no_matching_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        eval_groups,
        "_load_groups",
        lambda: [{"g": "Only", "cat": "other", "items": []}],
    )

    result = eval_groups.run_groups_eval(category="missing")

    assert result["ok"] is True
    assert result["summary"] == {
        "groups": 0,
        "items": 0,
        "asserted_items": 0,
        "unasserted_items": 0,
        "assertion_checks": 0,
        "failed_items": 0,
        "source_checks": 0,
        "source_marker_checks": 0,
        "failed_source_checks": 0,
        "failed_checks": 0,
    }


def test_groups_eval_cli_serializes_filtered_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = io.StringIO()
    calls: list[tuple[str | None, str | None]] = []

    def fake_run_groups_eval(
        *, category: str | None = None, group_name: str | None = None
    ) -> dict[str, object]:
        calls.append((category, group_name))
        return {"ok": False, "summary": {"failed_checks": 1}, "results": []}

    monkeypatch.setattr(eval_groups, "run_groups_eval", fake_run_groups_eval)
    monkeypatch.setattr(eval_groups.sys, "stdout", output)

    assert eval_groups.main(["--category", "target", "--group", "Focus"]) == 1
    assert calls == [("target", "Focus")]
    assert json.loads(output.getvalue()) == {
        "ok": False,
        "summary": {"failed_checks": 1},
        "results": [],
    }
