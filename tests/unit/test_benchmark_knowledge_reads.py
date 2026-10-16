"""Tests for benchmark result summaries and comparisons."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.benchmark_knowledge_reads import (
    compare_reports,
    main,
    run_suite,
    summarize,
)
from soulmap.runtime.knowledge.keyword_lists import _read_markdown_text_cached


def test_summarize_reports_stable_statistics() -> None:
    result = summarize([1.0, 2.0, 3.0])

    assert result["min_seconds"] == 1.0
    assert result["median_seconds"] == 2.0
    assert result["mean_seconds"] == 2.0
    assert result["max_seconds"] == 3.0
    assert result["stdev_seconds"] == pytest.approx(1.0)


def test_summarize_rejects_empty_samples() -> None:
    with pytest.raises(ValueError, match="At least one"):
        summarize([])


def test_compare_reports_marks_regression_and_improvement() -> None:
    baseline = {
        "benchmarks": {
            "slower": {"median_seconds": 2.0},
            "faster": {"median_seconds": 4.0},
        }
    }
    current = {
        "benchmarks": {
            "slower": {"median_seconds": 3.0},
            "faster": {"median_seconds": 2.0},
            "new": {"median_seconds": 1.0},
        }
    }

    result = compare_reports(baseline, current)

    assert result["slower"]["change_pct"] == pytest.approx(50.0)
    assert result["slower"]["direction"] == "slower"
    assert result["faster"]["change_pct"] == pytest.approx(-50.0)
    assert result["faster"]["direction"] == "faster_or_equal"
    assert result["new"]["status"] == "invalid"
    assert result["new"]["direction"] == "not_comparable"


@pytest.mark.parametrize(
    "bad_median",
    [0, 0.0, -1.0, float("nan"), float("inf"), None, "fast", True],
)
def test_compare_reports_flags_invalid_baseline_median(bad_median: object) -> None:
    baseline = {"benchmarks": {"case": {"median_seconds": bad_median}}}
    current = {"benchmarks": {"case": {"median_seconds": 1.0}}}

    result = compare_reports(baseline, current)["case"]

    assert result["status"] == "invalid"
    assert result["direction"] == "not_comparable"
    assert "change_pct" not in result


def test_compare_reports_flags_invalid_or_missing_current_median() -> None:
    baseline = {
        "benchmarks": {
            "missing": {"median_seconds": 1.0},
            "invalid": {"median_seconds": 1.0},
        }
    }
    current = {
        "benchmarks": {
            "missing": {},
            "invalid": {"median_seconds": 0.0},
        }
    }

    result = compare_reports(baseline, current)

    assert result["missing"]["status"] == "invalid"
    assert result["invalid"]["status"] == "invalid"


def test_compare_reports_flags_missing_workload_on_either_side() -> None:
    result = compare_reports(
        {"benchmarks": {"only_baseline": {"median_seconds": 1.0}}},
        {"benchmarks": {"only_current": {"median_seconds": 1.0}}},
    )

    assert result["only_baseline"]["status"] == "invalid"
    assert result["only_current"]["status"] == "invalid"


def test_run_suite_leaves_markdown_cache_empty() -> None:
    run_suite(warmups=0, iterations=1)

    assert _read_markdown_text_cached.cache_info().currsize == 0


def test_invalid_baseline_never_trips_regression_gate(tmp_path: Path) -> None:
    names = (
        "uncached_two_table_reads",
        "cold_cache_two_table_loads",
        "warm_cache_two_table_loads",
    )
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps({"benchmarks": {name: {"median_seconds": 0} for name in names}}),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--warmups",
            "0",
            "--iterations",
            "1",
            "--output",
            str(tmp_path / "current.json"),
            "--compare",
            str(baseline),
            "--fail-on-regression",
            "0",
        ]
    )

    assert exit_code == 0
