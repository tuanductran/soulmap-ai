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
`artifacts/benchmarks/markdown-reads.json` (ignored/generated output should not be
committed) and prints median, mean, and standard deviation.

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
- **Cold cache:** clear the shared Markdown text cache, then load both tables.
- **Warm cache:** load both tables after the cache is primed.

It records Python implementation/version, platform, processor, run parameters,
timestamp, and timing statistics in JSON. Compare reports from the same machine,
Python version, power mode, and workload whenever possible. Close noisy workloads
and repeat suspicious results.

This is intentionally a focused benchmark for the recent repeated-read optimization,
not a full application latency suite. It does not claim a speedup until reports are
collected and compared. A cold-cache sample includes cache invalidation and filesystem
metadata checks; the warm-cache path still checks file metadata to invalidate stale
content. Benchmark numbers are observational and should not be used as strict CI
thresholds across heterogeneous runners.
