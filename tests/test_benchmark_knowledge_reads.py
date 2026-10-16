"""Regression tests for the Markdown cache benchmark harness."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts import benchmark_knowledge_reads as benchmark
from scripts.benchmark_knowledge_reads import compare_reports, run_suite, summarize
from soulmap.runtime.knowledge.keyword_lists import (
    _read_markdown_text_cached,
    extract_table_rows,
    load_table_rows,
)
from soulmap.runtime.source_registry import runtime_skill_path


def test_cached_table_rows_match_uncached_parser() -> None:
    """Caching must not change parsed table content for benchmark workloads."""
    markdown_path = runtime_skill_path("pattern-mapper")
    source = markdown_path.read_text(encoding="utf-8")

    for heading in ("Scoring", "Runtime guidance"):
        _read_markdown_text_cached.cache_clear()
        assert load_table_rows(markdown_path, heading) == extract_table_rows(
            source, heading
        )
        assert extract_table_rows(source, heading)


def test_markdown_cache_invalidates_when_file_version_changes(tmp_path: Path) -> None:
    """A changed file version must not reuse rows parsed from stale text."""
    markdown_path = tmp_path / "example.md"
    markdown_path.write_text(
        "## Scoring\n\n| Rule | Value |\n| --- | --- |\n| Weight | 1 |\n",
        encoding="utf-8",
    )
    _read_markdown_text_cached.cache_clear()
    assert load_table_rows(markdown_path, "Scoring") == (("Weight", "1"),)

    markdown_path.write_text(
        "## Scoring\n\n| Rule | Value |\n| --- | --- |\n| Weight | 200 |\n",
        encoding="utf-8",
    )
    assert load_table_rows(markdown_path, "Scoring") == (("Weight", "200"),)
    _read_markdown_text_cached.cache_clear()


def test_summarize_reports_median_and_single_sample_dispersion() -> None:
    """The report summary must handle a single timing sample deterministically."""
    result = summarize([0.25])

    assert result["sample_count"] == 1
    assert result["median_seconds"] == 0.25
    assert result["mean_seconds"] == 0.25
    assert result["stdev_seconds"] == 0.0


def test_compare_reports_flags_only_comparable_median_changes() -> None:
    """Missing or invalid benchmark baselines must remain non-comparable."""
    baseline: dict[str, Any] = {
        "benchmarks": {
            "warm": {"median_seconds": 1.0},
            "bad": {"median_seconds": 0.0},
        }
    }
    current: dict[str, Any] = {
        "benchmarks": {
            "warm": {"median_seconds": 1.2},
            "bad": {"median_seconds": 1.0},
            "new": {"median_seconds": 0.5},
        }
    }

    comparisons = compare_reports(baseline, current)

    assert comparisons["warm"]["status"] == "ok"
    assert abs(comparisons["warm"]["change_pct"] - 20.0) < 1e-9
    assert comparisons["bad"]["status"] == "invalid"
    assert comparisons["new"]["status"] == "invalid"


def test_cached_detector_knowledge_matches_uncached_parsing() -> None:
    """Representative detector loaders must preserve Markdown semantics."""
    _read_markdown_text_cached.cache_clear()
    assert benchmark._cached_detector_knowledge_loads() == (
        benchmark._uncached_detector_knowledge_loads()
    )
    _read_markdown_text_cached.cache_clear()


def test_benchmark_suite_emits_all_expected_workloads() -> None:
    """The benchmark entrypoint must execute and report each comparison mode."""
    report = run_suite(warmups=0, iterations=1)

    assert report["schema_version"] == 1
    assert report["parameters"] == {"warmups": 0, "iterations": 1}
    assert set(report["benchmarks"]) == {
        "uncached_two_table_reads",
        "cold_cache_two_table_loads",
        "warm_cache_two_table_loads",
        "uncached_detector_knowledge_loads",
        "cold_cache_detector_knowledge_loads",
        "warm_cache_detector_knowledge_loads",
    }
    assert all(result["sample_count"] == 1 for result in report["benchmarks"].values())
    assert all(result["median_seconds"] > 0 for result in report["benchmarks"].values())
    assert set(report["workload"]["timing_scope"]) == set(report["benchmarks"])
    assert "end-to-end" in report["workload"]["comparison_note"]
    timing_scope = report["workload"]["timing_scope"][
        "warm_cache_detector_knowledge_loads"
    ]
    assert "Path.resolve()" in timing_scope
    assert "Path.stat()" in timing_scope
