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

## Adding or Editing SKILL.md Files

When creating or updating a `SKILL.md` in `skills/`, `templates/`, or `.claude/skills/`,
follow these rules. They are enforced by `tests/test_skill_metadata_contract.py`.

### Frontmatter requirements

```yaml
---
name: "hyphenated-short-name"
description: Third-person summary. Relevant for [task types].
license: Complete terms in LICENSE
---
```

**name:** Lowercase, hyphen-separated, 64 characters max. No underscores.

**description:** Third-person only. Never open with "Use this when" or "Use when" --
these are imperative instructions, not descriptions. The description is injected into the
system prompt as metadata; mixing imperative language degrades routing reliability.

```yaml
# Correct
description: SoulMap AI safety rules covering crisis handling and dependency prevention.
  Relevant for requests involving harm, escalation, or refusal behavior.

# Wrong
description: SoulMap AI safety rules. Use this when a request involves harm.
```

**license:** Always `Complete terms in LICENSE`. Do not omit.

### Invocation controls for side-effect skills

If a skill triggers real-world side effects (publishing, releasing, deploying), add
`disable-model-invocation: true` after the description line:

```yaml
---
name: release-readiness-review
description: ...
disable-model-invocation: true
---
```

### Build contract

After adding any `.md` to `skills/` or `templates/`, run the appropriate command(s) to rebuild the distribution artifacts:

```bash
# To build the standard .zip archive
python -m tools.build_skill

# To build the .skill package for Claude
python -m tools.build_skill --skill
```

`tests/test_build_artifacts.py::test_new_skill_files_appear_in_built_archive` will fail
if the new file is missing from the rebuilt archive.
