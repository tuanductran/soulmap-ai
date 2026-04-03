---
name: github-actions-maintainer
description: Review or update GitHub Actions workflows for SoulMap AI, especially CI, release, CodeQL, permissions, concurrency, and actionlint-safe changes that should stay aligned with existing repo tooling.
disable-model-invocation: true
---

# GitHub Actions maintainer

Use this skill when working on:

- files under `.github/workflows/`
- CI failures tied to workflow syntax or job design
- GitHub Actions permissions, concurrency, caching, or artifact handling
- release automation
- CodeQL workflow maintenance

## Sources to check first

- `../rules/github-actions.md`
- `../rules/repo-workflow.md`
- `../rules/python-tooling.md`
- `.github/workflows/`
- `src/soulmap/devtools/`
- `docs/engineering/DEV.md`
- `docs/operations/OPERATIONS.md`

## Do not use this skill for

- application Python changes that do not affect CI or release automation
- SoulMap product behavior, voice, brand, or safety content
- release-readiness review without any workflow editing
- generic repository planning when no GitHub Actions surface is involved

## What good looks like

- smallest correct workflow diff
- least-privilege permissions
- stable triggers
- clear concurrency behavior
- reuse of existing repo commands
- local validation that mirrors CI

## Workflow

1. Read the target workflow and the adjacent workflows first.
2. Identify whether the change affects triggers, permissions, concurrency, caching,
   artifacts, or release semantics.
3. Reuse existing repository commands rather than duplicating logic in shell.
4. Keep official GitHub actions aligned with current repo conventions.
5. Explain any new third-party action or permission increase explicitly.
6. Run the matching local validation commands after the edit.

## Validation

Always run:

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap test -n auto -q
```

Add these when relevant:

```bash
uv run soulmap eval-groups
uv run soulmap markdown-contract --root .
uv run soulmap build
uv run soulmap build --skill
```

If `actionlint` is available, run it after changing workflow files.

## Definition of done

The workflow update is done when:

- the diff is limited to the GitHub Actions surface that actually changed
- triggers, permissions, and concurrency behavior are explicit
- existing repository commands are reused instead of duplicated
- any new third-party action or permission increase is justified
- the relevant local checks pass
