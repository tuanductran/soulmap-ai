# Contributing

## Setup

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
```

If you forget to activate `.venv`, the `python -m tools.*` commands will try to use the
repo's local `.venv` automatically (and print a small notice) to avoid confusing
"missing dependency" errors from a system Python.

## Format & Lint

```bash
source .venv/bin/activate
bash scripts/format.sh
bash scripts/lint.sh
python -m pytest
```

## Brand Consistency

Before merging, confirm that any changes to positioning, safety, or templates remain
consistent across:

- [README.md](README.md)
- [skills/brand/SKILL.md](skills/brand/SKILL.md)
- [templates/SKILL.md](templates/SKILL.md)
- [skills/brand/message-hierarchy.md](skills/brand/message-hierarchy.md)
- [skills/brand/surfaces-and-scope.md](skills/brand/surfaces-and-scope.md)
- [skills/brand/brand-positioning.md](skills/brand/brand-positioning.md)
- [templates/brand-copy.md](templates/brand-copy.md)
- [templates/onboarding-copy.md](templates/onboarding-copy.md)
- [templates/demo-scenarios.md](templates/demo-scenarios.md)
- [templates/launch-readiness-checklist.md](templates/launch-readiness-checklist.md)

## Markdown contract

This repo enforces a small set of Markdown constraints to keep AI tooling and formatters
from breaking structure.

See [docs/content-contract.md](docs/content-contract.md).

## Pre-commit (optional)

If you use git for this repo:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files
```

## Versioning

- `pyproject.toml` (`[project].version`) is the canonical version for this repo.
- Update [CHANGELOG.md](CHANGELOG.md) under "Unreleased" with every meaningful change.
- Bump the version in `pyproject.toml` when you make a release:
  - Patch: wording fixes, non-breaking detector tweaks.
  - Minor: new frameworks, new detectors, or expanded policies.
  - Major: behavioral breaking changes in safety rules or response structure.
