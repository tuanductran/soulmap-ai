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

## Repository consistency and comment audit

Run the repository-wide inventory from a clean checkout:

```bash
uv run python scripts/audit_repo_consistency.py --history
```

For a focused pull-request audit, compare against the current base ref:

```bash
git fetch origin main
uv run python scripts/audit_repo_consistency.py --base origin/main
```

The report inventories references to paths deleted in the selected Git range and
comment-only markers such as `TODO`, `FIXME`, `HACK`, `XXX`, temporary notes,
and obsolete/migration markers. It is a candidate inventory, not an auto-cleaner:
inspect each match in context and classify it as remove, rewrite, keep, or track
separately. Historical ADRs, changelogs, test fixtures, intentional compatibility
notes, legal notices, and tool directives may legitimately mention old names or
markers. Never delete a comment solely because it matches a keyword.

When a path was deleted, search for both its exact repository path and distinctive
basename references. Confirm each candidate against the current tree and source of
truth before editing. For a comment cleanup, remove only redundant narration or
commented-out code whose intent is fully recoverable from Git history; preserve
rationale that explains a current invariant. Review the diff, then run the normal
format, lint, link/Markdown checks, and relevant tests.

For setup and workflow details, use [`docs/engineering/DEV.md`](../docs/engineering/DEV.md).
