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
- [SKILL.md](SKILL.md)
- [skills/brand/message_hierarchy.md](skills/brand/message_hierarchy.md)
- [skills/brand/surfaces_and_scope.md](skills/brand/surfaces_and_scope.md)
- [skills/brand/brand_positioning.md](skills/brand/brand_positioning.md)
- [templates/brand_copy.md](templates/brand_copy.md)
- [templates/onboarding_copy.md](templates/onboarding_copy.md)
- [templates/demo_scenarios.md](templates/demo_scenarios.md)
- [templates/launch_readiness_checklist.md](templates/launch_readiness_checklist.md)

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
