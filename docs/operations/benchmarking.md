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

Each timed sample runs the same two table parses. The cache-cold path includes cache
clearing and the first file load; the cache-warm setup is outside the timed sample.
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
