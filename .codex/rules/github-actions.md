# Codex GitHub Actions Rules

Use these rules when Codex edits files in `.github/workflows/` or related workflow
automation.

## Working Rules

- Read the target workflow and compare it with the other existing workflows first.
- Prefer the repository's tested Python tooling commands over new inline shell logic.
- Preserve least-privilege `permissions`, defaulting to `contents: read` unless a job
  needs more.
- Keep or add `concurrency` where stale runs should be canceled.
- Follow the repository's existing patterns for Python setup, caching, build, and
  artifact upload.
- Do not introduce new third-party actions casually. If one is necessary, explain why
  and prefer pinned versions already trusted in the repo.

## Validation

After meaningful workflow edits, run the relevant local checks:

```bash
python3 -m tools.format
python3 -m tools.lint
python3 -m pytest -q
```

When the workflow touches CI, release, packaging, or markdown validation, also run the
same commands the workflow relies on, such as:

```bash
python3 -m tools.eval_groups
python3 -m tools.eval_conversations
python3 -m modules.markdown_contract --root .
python3 -m tools.build_skill
python3 -m tools.build_skill --skill
```

If `actionlint` is available, run it after editing `.github/workflows/`.
