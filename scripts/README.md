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

## Python reachability inventory

Run the conservative source-module inventory from the repository root:

```bash
uv run python scripts/audit_python_reachability.py
uv run python scripts/audit_python_reachability.py --entry soulmap.cli --entry soulmap.runtime.detectors.crisis_detector
```

The inventory starts from declared Python entry modules, follows static local imports,
package initializers, and literal `importlib.import_module(...)`, `import_module(...)`,
or `__import__(...)` calls. Modules outside that graph are **review candidates only**.
It does not prove files or symbols are unused and must never drive automated deletion.
Computed dynamic imports, test/script-only consumers, entry-point metadata, registry
conventions, non-Python callers, and files loaded by path are not fully inferred.

Keep the audit categories separate:

- **Python module reachability:** this inventory; candidates are not deletion evidence.
- **Unused symbols / unreachable statements:** Vulture provides confidence-scored
  symbol-level findings, not a complete repository file reachability graph.
- **Dependency declarations:** Deptry compares Python imports with project dependency
  metadata; it does not establish whether a local module or Markdown resource is used.
- **Stale references to deleted paths:** `audit_repo_consistency.py` scans Git history
  and tracked text for likely references; matches still require contextual review.
- **Canonical knowledge and indirectly loaded resources:** `skills/`, registry data,
  Markdown contracts, templates, prompts, schemas, and package inclusion are governed by
  the existing knowledge audits, contract tests, registry tests, and build verification.
  This Python-only graph must not classify these resources as unused.

Knip is a useful design reference for explicit entry points, recursive graph expansion,
and configuration/plugin-aware discovery, but its documented analyzer targets JavaScript
and TypeScript ecosystems. Do not add Knip as a dependency or treat it as a Python,
Markdown, or SoulMap registry analyzer. Its key lesson here is that accurate reachability
depends on discovering entry points and non-import references before interpreting
unreachable candidates.

## Resource reachability inventory

Run the resource inventory separately from the Python import graph:

```bash
uv run python scripts/audit_resource_inventory.py
```

It records resources under `skills/`, `templates/`, local maintainer prompts/skills/rules,
plugin metadata, evaluation datasets, schemas (when present), and the root shipped
knowledge files. Evidence labels distinguish runtime registry edges, literal path
references, local Markdown links, package inclusion, and local-maintainer conventions.
A missing target in the canonical runtime registry is an error; resources without a
static edge remain review-only, not proven unused. Dynamic loaders, product conventions,
external consumers, and human-selected prompts cannot be fully inferred by this scan.
Use it alongside the existing knowledge ownership audit, Markdown contracts, registry
tests, build verification, and Python module inventory; never use it to auto-delete files.

## Resource reachability inventory

Run the resource inventory separately from the Python import graph:

```bash
uv run python scripts/audit_resource_inventory.py
```

It records resources under `skills/`, `templates/`, local maintainer prompts/skills/rules,
plugin metadata, evaluation datasets, documentation, schemas (when present), and the root
shipped knowledge files. Evidence labels distinguish runtime registry edges, literal path
references, local Markdown links, package inclusion, and local-maintainer conventions.
A missing target in the canonical runtime registry is an error; resources without a
static edge remain review-only, not proven unused. Dynamic loaders, product conventions,
external consumers, and human-selected prompts cannot be fully inferred by this scan.
Use it alongside the existing knowledge ownership audit, Markdown contracts, registry
tests, build verification, and Python module inventory; never use it to auto-delete files.

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
basename references. The history mode also derives ancestor directories that no
longer contain tracked files and checks for path-shaped references using directory
boundaries, including forward- and backslash separators and quoted standalone
root-directory tokens. This catches stale folder references without treating every
ordinary prose mention as a path. All matches remain review candidates.

Confirm each candidate against the current tree and source of truth before editing.
For a comment cleanup, remove only redundant narration or commented-out code whose
intent is fully recoverable from Git history; preserve rationale that explains a
current invariant. Review the diff, then run the normal format, lint, link/Markdown
checks, and relevant tests.

For setup and workflow details, use [`docs/engineering/DEV.md`](../docs/engineering/DEV.md).
