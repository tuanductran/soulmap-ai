# Scripts

This folder contains the small set of shell and Python helpers that have distinct
local-workflow or CI consumers. Canonical developer commands live in the `soulmap` CLI
implemented under `src/soulmap/devtools/`.

## Setup

```bash
bash scripts/bootstrap_venv.sh
```

Activating `.venv` is optional when you use `uv run ...`. To activate it in the
current shell, source this helper rather than running it:

```bash
source scripts/activate_venv.sh
```

Cross-platform equivalents are the canonical Python entrypoints:

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap check-api-docs --root .
uv run soulmap build
uv run soulmap build --skill
uv run soulmap library-manifest
uv run python scripts/verify_artifact_hashes.py
uv run python scripts/verify_extracted_artifacts.py
uv run soulmap release-verify --root .
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run soulmap eval-markdown-contracts
```

`release-verify` is the canonical release gate. It performs a clean artifact build,
checks package and integration versions against `pyproject.toml`, verifies every
supported integration guide uses `SOULMAP.md`, checks the exact shipped archive
members, and validates the Library manifest's artifact sizes and SHA-256 values.
It also writes `dist/release-verification.json` as a machine-readable summary.

If you edit public URLs in Markdown and want live external validation, run:

```bash
uv run soulmap check-links --root . --check-external
```

Before pushing, mirror the local CI core with:

```bash
uv run soulmap lint --skip-tests
uv run soulmap test -n auto -q
```

CI and release verification use the reproducibility helper to record an explicit
pytest-randomly seed and preserve a serial reproduction command when parallel tests fail:

```bash
uv run python scripts/pytest_diagnostics.py
```

After building the Library artifacts, verify their recorded size and SHA-256 values
without network access:

```bash
uv run soulmap library-manifest
uv run python scripts/verify_artifact_hashes.py
```

For setup and workflow details, use [`docs/engineering/DEV.md`](../docs/engineering/DEV.md).
