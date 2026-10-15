"""Benchmark repeated Markdown reads in the SoulMap runtime.

The harness intentionally uses only the Python standard library so maintainers
can run it in the locked project environment without adding a benchmark dependency.
"""

from __future__ import annotations

import argparse
import json
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


def compare_reports(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, dict[str, float | str]]:
    """Compare matching benchmark medians; positive change means slower."""
    baseline_results = baseline.get("benchmarks", {})
    current_results = current.get("benchmarks", {})
    comparisons: dict[str, dict[str, float | str]] = {}
    for name in sorted(set(baseline_results) & set(current_results)):
        before = float(baseline_results[name]["median_seconds"])
        after = float(current_results[name]["median_seconds"])
        change_pct = ((after - before) / before * 100.0) if before else 0.0
        comparisons[name] = {
            "baseline_median_seconds": before,
            "current_median_seconds": after,
            "change_pct": change_pct,
            "direction": "slower" if change_pct > 0 else "faster_or_equal",
        }
    return comparisons


def _measure(
    operation: Benchmark, *, warmups: int, iterations: int
) -> dict[str, float]:
    for _ in range(warmups):
        operation()
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        samples.append(time.perf_counter() - start)
    return summarize(samples)


def run_suite(*, warmups: int, iterations: int) -> dict[str, Any]:
    """Run the same two-table workload with uncached, cold-cache and warm-cache reads."""
    markdown_path = runtime_skill_path("pattern-mapper")

    def uncached_multi_table() -> None:
        for heading in TABLE_HEADINGS:
            extract_table_rows(markdown_path.read_text(encoding="utf-8"), heading)

    def cold_cache_multi_table() -> None:
        _read_markdown_text_cached.cache_clear()
        for heading in TABLE_HEADINGS:
            load_table_rows(markdown_path, heading)

    def warm_cache_multi_table() -> None:
        for heading in TABLE_HEADINGS:
            load_table_rows(markdown_path, heading)

    # Prime the file cache before measuring warm-cache behavior.
    _read_markdown_text_cached.cache_clear()
    for heading in TABLE_HEADINGS:
        load_table_rows(markdown_path, heading)

    benchmarks = {
        "uncached_two_table_reads": _measure(
            uncached_multi_table, warmups=warmups, iterations=iterations
        ),
        "cold_cache_two_table_loads": _measure(
            cold_cache_multi_table, warmups=warmups, iterations=iterations
        ),
        "warm_cache_two_table_loads": _measure(
            warm_cache_multi_table, warmups=warmups, iterations=iterations
        ),
    }
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
                "same file; compare direct reads, cache-cold loads, and cache-warm loads."
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
            print(
                f"{name}: {result['change_pct']:+.2f}% "
                f"({result['direction']})"
            )
        if args.fail_on_regression is not None and any(
            float(result["change_pct"]) > args.fail_on_regression
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
