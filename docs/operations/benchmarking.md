# Python benchmark harness

The benchmark harness measures repeated Markdown table reads and representative
detector knowledge-loading patterns without adding a runtime or development dependency. It is a diagnostic tool, not a unit test and
not a CI gate by default.

## Run

From the repository root:

```bash
uv run python scripts/benchmark_knowledge_reads.py
```

The command writes a JSON report to
`artifacts/benchmarks/markdown-reads.json` (git-ignored generated output; do not
commit it) and prints median, mean, and standard deviation.

Use more iterations for a steadier local comparison:

```bash
uv run python scripts/benchmark_knowledge_reads.py --warmups 5 --iterations 100
```

Compare with a previously captured report:

```bash
uv run python scripts/benchmark_knowledge_reads.py \
  --output artifacts/benchmarks/current.json \
  --compare artifacts/benchmarks/baseline.json
```

Optionally fail when any comparable benchmark median regresses beyond a threshold:

```bash
uv run python scripts/benchmark_knowledge_reads.py \
  --output artifacts/benchmarks/current.json \
  --compare artifacts/benchmarks/baseline.json \
  --fail-on-regression 10
```

## Workload and interpretation

The harness loads the `Scoring` and `Runtime guidance` tables from the canonical
`skills/frameworks/pattern-mapper.md` source in three modes:

- **Uncached:** read the Markdown file independently for each table.
- **Cache-cold:** clear the shared text cache, then load both tables. This is one
  cache miss followed by one hit because both tables come from the same file.
- **Cache-warm:** prime the text cache before the timer starts, then load both tables.

Each timed sample runs the same two table parses. Cache clearing and cache priming
are setup work outside the timer; the cache-cold path measures the first file load
plus the second cache hit.
Workloads are interleaved in rotating order to reduce fixed-order and drift bias.
The uncached path intentionally models the pre-cache implementation and therefore
does not perform the metadata checks required by the cache.

The report records Python implementation/version, platform, processor, run
parameters, timestamp, and timing statistics. Compare reports from the same machine,
Python version, power mode, and workload whenever possible. Close noisy workloads
and repeat suspicious results. This is a focused diagnostic benchmark, not a full
application latency suite or a CI gate by default.

A report comparison whose baseline or current median is missing, non-numeric,
non-finite, or not strictly positive is marked `not comparable`; a workload present
on only one side is also marked `not comparable`. These cases are never shown as
`0%` change and never trip `--fail-on-regression`. The shared Markdown cache is
cleared when the suite finishes.

Most of the measured time may be table parsing (`extract_table_rows`), which is not
cached. The warm path still checks file metadata to invalidate stale content, so on
a warm OS page cache the metadata checks can cost as much as the file read they
replace. Results are observational and should not be treated as strict thresholds
across heterogeneous runners.

### Detector workload and cache comparison

The detector suite spans four canonical Markdown sources: empath boundary, ancestral
patterns, somatic wellbeing, and pattern mapper. Before timing, the harness verifies that
cached values match both uncached parsing paths.

It reports three distinct detector comparisons:

- **Batch baseline** (`uncached_detector_knowledge_loads`): reads each source once,
  then parses multiple sections from in-memory text. This models batching, not the
  current per-section loader call pattern.
- **Equivalent uncached loader calls** (`uncached_detector_loader_calls`): follows
  the same per-section call pattern and parses the same values as the cached variant,
  but reads Markdown directly on every call instead of using the text cache.
- **Production cache cold/warm** (`cold_cache_detector_knowledge_loads` and
  `warm_cache_detector_knowledge_loads`): calls the production loaders per section.
  Cold mode clears the cache before timing; warm mode primes it before timing.

For the closest estimate of the cache's net effect under the current loader pattern,
compare `uncached_detector_loader_calls` with
`warm_cache_detector_knowledge_loads`. This is not a pure measurement of file-read
cost: the cached path still resolves paths and calls `Path.stat()` for cache
invalidation, while the uncached path performs direct reads. The batch baseline is
useful for evaluating a future batching change, but must not be used alone to claim
that caching itself is faster or slower.

The JSON report records a `workload.timing_scope` entry for each benchmark so the
included path resolution, metadata checks, reads, parsing, and setup boundaries remain
explicit. These microbenchmarks are still not an actual request-path latency suite;
retain or remove the cache only when comparable results and representative request-path
measurements justify that decision.
