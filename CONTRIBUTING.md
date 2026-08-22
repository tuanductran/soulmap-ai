# Contributing

## Setup

```bash
uv python install 3.11
bash scripts/bootstrap_venv.sh
```

Activating `.venv` is optional when you use `uv run ...`. This repo standardizes on
Python 3.11 for local development and CI.

## Format and lint

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap test
```

On macOS/Linux the shell scripts delegate to the canonical `uv run soulmap ...`
commands.

## Brand Consistency

Before merging, confirm that any changes to positioning, safety, or templates remain
consistent across:

- [README.md](README.md)
- [skills/brand/SKILL.md](skills/brand/SKILL.md)
- [templates/README.md](templates/README.md) (internal-only, not shipped)
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

See [docs/engineering/content-contract.md](docs/engineering/content-contract.md).

Ordered lists should stay sequential (`1. 2. 3.`), not normalized to repeated `1.`.

## Git hooks (optional)

If you use git for this repo:

```bash
lefthook install
lefthook run pre-commit
```

`lefthook` installs both the `pre-commit` and `commit-msg` hooks. Use
`uv run soulmap check-links --root . --check-external`
separately when a change edits public URLs and you want live external URL validation.
This repo intentionally does not run a heavy `pre-push` hook. Before pushing, run
`uv run soulmap lint --skip-tests` and
`uv run soulmap test -n auto -q` yourself.

## Soulmate custom skills

Developers building framework-neutral foundation skills should follow
[`packages/soulmate/CONTRIBUTING.md`](packages/soulmate/CONTRIBUTING.md). It is separate from
root SoulMap Skills and covers Soulmate ownership, manifest registration, artifact boundaries,
security tests, deterministic build/verify commands, and the review checklist.

## Versioning

- `pyproject.toml` (`[project].version`) is the canonical version for this repo.
- Update [CHANGELOG.md](CHANGELOG.md) under "Unreleased" with every meaningful change.
- Bump the version in `pyproject.toml` when you make a release:
  - Patch: wording fixes, non-breaking detector tweaks.
  - Minor: new frameworks, new detectors, or expanded policies.
  - Major: behavioral breaking changes in safety rules or response structure.

## Adding or Editing SKILL.md Files

When creating or updating a `SKILL.md` in `skills/` or `.claude/skills/`,
follow these rules. Treat them as repo contract rules and verify them through the
normal formatting and linting flow.

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
system prompt as metadata: mixing imperative language degrades routing reliability.

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

After adding any `.md` to `skills/`, run the appropriate command(s) to rebuild the distribution artifacts. (`templates/` is internal-only and is excluded from the build.)

```bash
# To build the standard .zip archive
uv run soulmap build

# To build the .skill package for Claude
uv run soulmap build --skill
```

If the new file is missing from the rebuilt archive, the build or packaging validation
steps should be treated as failed and fixed before release.
