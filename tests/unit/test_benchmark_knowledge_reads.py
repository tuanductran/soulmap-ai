"""Tests for benchmark result summaries and comparisons."""

from __future__ import annotations

import pytest

from scripts.benchmark_knowledge_reads import compare_reports, summarize


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
    assert "new" not in result
