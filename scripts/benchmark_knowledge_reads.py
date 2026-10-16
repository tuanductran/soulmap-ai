"""Benchmark repeated Markdown reads in the SoulMap runtime.

The harness intentionally uses only the Python standard library so maintainers
can run it in the locked project environment without adding a benchmark dependency.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from soulmap.runtime.knowledge.keyword_lists import (
    _read_markdown_text_cached,
    extract_table_rows,
    load_table_rows,
)
from soulmap.runtime.source_registry import runtime_skill_path

Benchmark = Callable[[], object]
TABLE_HEADINGS = ("Scoring", "Runtime guidance")


def summarize(samples_seconds: list[float]) -> dict[str, float]:
    """Summarize wall-clock samples using robust and familiar statistics."""
    if not samples_seconds:
        raise ValueError("At least one timing sample is required.")
    return {
        "min_seconds": min(samples_seconds),
        "median_seconds": statistics.median(samples_seconds),
        "mean_seconds": statistics.fmean(samples_seconds),
        "max_seconds": max(samples_seconds),
        "stdev_seconds": (
            statistics.stdev(samples_seconds) if len(samples_seconds) > 1 else 0.0
        ),
    }


def _valid_median(results: dict[str, Any], name: str) -> float | None:
    """Return a finite, positive median for a benchmark, or None if unusable."""
    entry = results.get(name)
    if not isinstance(entry, dict):
        return None
    value = entry.get("median_seconds")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    median = float(value)
    return median if math.isfinite(median) and median > 0.0 else None


def compare_reports(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Compare reports; positive change means slower.

    Missing benchmark names and invalid medians are explicitly not comparable,
    never treated as zero change, and never trigger the regression gate.
    """
    baseline_results = baseline.get("benchmarks", {})
    current_results = current.get("benchmarks", {})
    if not isinstance(baseline_results, dict):
        baseline_results = {}
    if not isinstance(current_results, dict):
        current_results = {}

    comparisons: dict[str, dict[str, Any]] = {}
    for name in sorted(set(baseline_results) | set(current_results)):
        before = _valid_median(baseline_results, name)
        after = _valid_median(current_results, name)
        if before is None or after is None:
            if name not in baseline_results:
                reason = "benchmark is missing from baseline"
            elif name not in current_results:
                reason = "benchmark is missing from current report"
            elif before is None:
                reason = "baseline median is missing, non-finite or not positive"
            else:
                reason = "current median is missing, non-finite or not positive"
            comparisons[name] = {
                "status": "invalid",
                "direction": "not_comparable",
                "reason": reason,
            }
            continue

        change_pct = (after - before) / before * 100.0
        comparisons[name] = {
            "status": "ok",
            "baseline_median_seconds": before,
            "current_median_seconds": after,
            "change_pct": change_pct,
            "direction": "slower" if change_pct > 0 else "faster_or_equal",
        }
    return comparisons


def _measure_interleaved(
    operations: dict[str, tuple[Callable[[], object] | None, Benchmark]],
    *,
    warmups: int,
    iterations: int,
) -> dict[str, dict[str, float]]:
    """Measure workloads in rotating order, running setup outside timed samples."""
    names = list(operations)
    samples: dict[str, list[float]] = {name: [] for name in names}

    def run_one(name: str, *, timed: bool) -> None:
        setup, operation = operations[name]
        if setup is not None:
            setup()
        if timed:
            start = time.perf_counter()
            operation()
            samples[name].append(time.perf_counter() - start)
        else:
            operation()

    # Rotate the starting workload each round to reduce fixed-order bias.
    for round_index in range(warmups):
        shift = round_index % len(names)
        for name in names[shift:] + names[:shift]:
            run_one(name, timed=False)

    for round_index in range(iterations):
        shift = round_index % len(names)
        for name in names[shift:] + names[:shift]:
            run_one(name, timed=True)

    return {name: summarize(values) for name, values in samples.items()}


def run_suite(*, warmups: int, iterations: int) -> dict[str, Any]:
    """Run comparable two-table workloads in an interleaved order."""
    markdown_path = runtime_skill_path("pattern-mapper")

    def uncached_multi_table() -> None:
        for heading in TABLE_HEADINGS:
            extract_table_rows(markdown_path.read_text(encoding="utf-8"), heading)

    def clear_cache() -> None:
        _read_markdown_text_cached.cache_clear()

    def cold_cache_multi_table() -> None:
        for heading in TABLE_HEADINGS:
            load_table_rows(markdown_path, heading)

    def prime_cache() -> None:
        _read_markdown_text_cached.cache_clear()
        # The text cache is keyed by file version, so one table load primes the
        # Markdown content for both timed table parses.
        load_table_rows(markdown_path, TABLE_HEADINGS[0])

    def warm_cache_multi_table() -> None:
        for heading in TABLE_HEADINGS:
            load_table_rows(markdown_path, heading)

    try:
        benchmarks = _measure_interleaved(
            {
                "uncached_two_table_reads": (None, uncached_multi_table),
                "cold_cache_two_table_loads": (clear_cache, cold_cache_multi_table),
                "warm_cache_two_table_loads": (prime_cache, warm_cache_multi_table),
            },
            warmups=warmups,
            iterations=iterations,
        )
    finally:
        # Leave the process-wide Markdown cache empty rather than primed.
        _read_markdown_text_cached.cache_clear()

    return {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "repository": "tuanductran/soulmap-ai",
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "parameters": {"warmups": warmups, "iterations": iterations},
        "workload": {
            "source": "skills/frameworks/pattern-mapper.md",
            "headings": list(TABLE_HEADINGS),
            "description": (
                "Load the Scoring and Runtime guidance Markdown tables from the "
                "same file. Uncached reads the file for each table; cache-cold "
                "clears the cache then performs one miss and one hit; cache-warm "
                "primes the cache outside the timed sample. Samples are interleaved."
            ),
        },
        "benchmarks": benchmarks,
    }


def _load_report(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "benchmarks" not in payload:
        raise ValueError(f"Not a SoulMap benchmark report: {path}")
    return payload


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Benchmark repeated Markdown table reads in SoulMap."
    )
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/benchmarks/markdown-reads.json"),
        help="Write a JSON report here (default: artifacts/benchmarks/markdown-reads.json).",
    )
    parser.add_argument(
        "--compare",
        type=Path,
        help="Compare this run with an earlier JSON report.",
    )
    parser.add_argument(
        "--fail-on-regression",
        type=float,
        metavar="PERCENT",
        help="Exit 1 if any comparable median is slower by more than this percentage.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run benchmarks, persist the report, and optionally compare with a baseline."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.warmups < 0 or args.iterations < 1:
        parser.error("--warmups must be >= 0 and --iterations must be >= 1")

    report = run_suite(warmups=args.warmups, iterations=args.iterations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Benchmark report: {args.output}")
    for name, result in report["benchmarks"].items():
        print(
            f"{name}: median={result['median_seconds'] * 1_000_000:.2f} µs "
            f"(mean={result['mean_seconds'] * 1_000_000:.2f} µs, "
            f"stdev={result['stdev_seconds'] * 1_000_000:.2f} µs)"
        )

    if args.compare:
        comparisons = compare_reports(_load_report(args.compare), report)
        if not comparisons:
            print("No matching benchmark names to compare.")
        for name, result in comparisons.items():
            if result["status"] != "ok":
                print(f"{name}: not comparable ({result['reason']})")
                continue
            print(f"{name}: {result['change_pct']:+.2f}% ({result['direction']})")
        if args.fail_on_regression is not None and any(
            result["status"] == "ok"
            and float(result["change_pct"]) > args.fail_on_regression
            for result in comparisons.values()
        ):
            print(
                f"Regression threshold exceeded: {args.fail_on_regression:.2f}%",
                file=sys.stderr,
            )
            return 1
    elif args.fail_on_regression is not None:
        parser.error("--fail-on-regression requires --compare")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
