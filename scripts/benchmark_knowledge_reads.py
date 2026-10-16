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
    extract_keyword_section,
    extract_labeled_groups,
    extract_table_rows,
    load_key_value_table,
    load_keyword_section,
    load_labeled_groups,
    load_table_rows,
)
from soulmap.runtime.source_registry import runtime_skill_path

Benchmark = Callable[[], object]
TABLE_HEADINGS = ("Scoring", "Runtime guidance")


def _uncached_key_value_table(text: str, heading: str) -> dict[str, str]:
    """Parse a strict two-column table without using the Markdown text cache."""
    rows = extract_table_rows(text, heading)
    if not rows or any(len(row) != 2 for row in rows):
        raise ValueError(f"Knowledge table {heading!r} must contain two columns.")
    values = {row[0]: row[1] for row in rows}
    if len(values) != len(rows) or any(not value for value in values.values()):
        raise ValueError(f"Knowledge table {heading!r} contains invalid entries.")
    return values


def _uncached_detector_knowledge_loads() -> dict[str, object]:
    """Load representative detector knowledge directly from Markdown files."""
    sources = {
        name: runtime_skill_path(name).read_text(encoding="utf-8")
        for name in (
            "empath-boundary",
            "ancestral-patterns",
            "somatic-wellbeing",
            "pattern-mapper",
        )
    }
    empath = sources["empath-boundary"]
    ancestral = sources["ancestral-patterns"]
    somatic = sources["somatic-wellbeing"]
    pattern = sources["pattern-mapper"]
    return {
        "empath.activation": extract_keyword_section(empath, "Activation Signals"),
        "empath.drain": extract_keyword_section(empath, "Drain signals"),
        "empath.people_context": extract_keyword_section(
            empath, "People-context signals"
        ),
        "empath.contract": _uncached_key_value_table(
            empath, "Runtime detection contract"
        ),
        "empath.guidance": _uncached_key_value_table(empath, "Guidance"),
        "ancestral.activation": extract_keyword_section(
            ancestral, "Activation Signals"
        ),
        "ancestral.groups": extract_labeled_groups(ancestral, "Detection signals"),
        "ancestral.scoring": _uncached_key_value_table(ancestral, "Scoring"),
        "ancestral.guidance": _uncached_key_value_table(ancestral, "Guidance"),
        "somatic.groups": extract_labeled_groups(somatic, "Detection signals"),
        "somatic.contract": _uncached_key_value_table(
            somatic, "Runtime detection contract"
        ),
        "somatic.guidance": _uncached_key_value_table(somatic, "Guidance"),
        "pattern.scoring": _uncached_key_value_table(pattern, "Scoring"),
        "pattern.guidance": _uncached_key_value_table(pattern, "Runtime guidance"),
    }


def _cached_detector_knowledge_loads() -> dict[str, object]:
    """Load the same representative detector knowledge through runtime loaders."""
    empath = runtime_skill_path("empath-boundary")
    ancestral = runtime_skill_path("ancestral-patterns")
    somatic = runtime_skill_path("somatic-wellbeing")
    pattern = runtime_skill_path("pattern-mapper")
    return {
        "empath.activation": load_keyword_section(empath, "Activation Signals"),
        "empath.drain": load_keyword_section(empath, "Drain signals"),
        "empath.people_context": load_keyword_section(empath, "People-context signals"),
        "empath.contract": load_key_value_table(empath, "Runtime detection contract"),
        "empath.guidance": load_key_value_table(empath, "Guidance"),
        "ancestral.activation": load_keyword_section(ancestral, "Activation Signals"),
        "ancestral.groups": load_labeled_groups(ancestral, "Detection signals"),
        "ancestral.scoring": load_key_value_table(ancestral, "Scoring"),
        "ancestral.guidance": load_key_value_table(ancestral, "Guidance"),
        "somatic.groups": load_labeled_groups(somatic, "Detection signals"),
        "somatic.contract": load_key_value_table(somatic, "Runtime detection contract"),
        "somatic.guidance": load_key_value_table(somatic, "Guidance"),
        "pattern.scoring": load_key_value_table(pattern, "Scoring"),
        "pattern.guidance": load_key_value_table(pattern, "Runtime guidance"),
    }


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
    """Run interleaved cache benchmarks for tables and detector knowledge."""
    markdown_path = runtime_skill_path("pattern-mapper")

    # Refuse to report timings if cache-backed production loaders change meaning.
    expected_knowledge = _uncached_detector_knowledge_loads()
    _read_markdown_text_cached.cache_clear()
    if _cached_detector_knowledge_loads() != expected_knowledge:
        raise AssertionError("Cached detector knowledge differs from uncached parsing")
    _read_markdown_text_cached.cache_clear()

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

    def clear_runtime_cache() -> None:
        _read_markdown_text_cached.cache_clear()

    def cold_cache_detector_knowledge() -> None:
        _cached_detector_knowledge_loads()

    def prime_runtime_cache() -> None:
        _read_markdown_text_cached.cache_clear()
        _cached_detector_knowledge_loads()

    def warm_cache_detector_knowledge() -> None:
        _cached_detector_knowledge_loads()

    try:
        benchmarks = _measure_interleaved(
            {
                "uncached_two_table_reads": (None, uncached_multi_table),
                "cold_cache_two_table_loads": (clear_cache, cold_cache_multi_table),
                "warm_cache_two_table_loads": (prime_cache, warm_cache_multi_table),
                "uncached_detector_knowledge_loads": (
                    None,
                    _uncached_detector_knowledge_loads,
                ),
                "cold_cache_detector_knowledge_loads": (
                    clear_runtime_cache,
                    cold_cache_detector_knowledge,
                ),
                "warm_cache_detector_knowledge_loads": (
                    prime_runtime_cache,
                    warm_cache_detector_knowledge,
                ),
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
            "detector_sources": [
                "skills/frameworks/empath-boundary.md",
                "skills/frameworks/ancestral-patterns.md",
                "skills/frameworks/somatic-wellbeing.md",
                "skills/frameworks/pattern-mapper.md",
            ],
            "description": (
                "Includes the original two-table microbenchmark and a representative "
                "detector knowledge workload spanning keyword sections, labeled "
                "groups, and key/value tables from empath, ancestral, somatic, and "
                "pattern-mapper Markdown. Cached and uncached outputs are compared "
                "before timing. Samples are interleaved; setup is outside timed samples."
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
