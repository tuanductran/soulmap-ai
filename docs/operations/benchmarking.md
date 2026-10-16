# Python benchmark harness

The benchmark harness measures the repeated Markdown table-read path without adding
a runtime or development dependency. It is a diagnostic tool, not a unit test and
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

### Representative detector workload limits

The detector workload is representative, not call-for-call equivalent. Its uncached
baseline reads each of four Markdown sources once and parses multiple sections from
those in-memory strings. The cold/warm variants use production loaders for each
section, which repeatedly resolve paths and check file metadata; cold mode reads each
source on its first loader call, while warm mode reuses cached text. The JSON report
includes a `workload.timing_scope` entry for each benchmark so this difference is
explicit in the evidence.

Do not infer that the cache improves overall detector latency from these microbenchmarks
alone. For example, the 2026-10-16 GitHub Actions run on CPython 3.11 reported a median
of about 1.40 ms for the batch-read uncached detector workload and 1.91 ms for the warm
production-loader workload. Those are different call patterns, not a controlled estimate
of cache overhead or proof that caching is harmful. The two-table microbenchmark also
showed only small differences on that runner. Treat these results as a reason to avoid
claiming a demonstrated speedup, not as grounds to remove the cache or alter runtime
behavior. A decision about cache value needs an equivalent workload comparison and,
ideally, measurements from actual request paths.
