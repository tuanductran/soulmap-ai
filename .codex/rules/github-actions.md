# GitHub Actions rules

Use these rules when editing GitHub Actions workflows or related automation.

## Sources of truth

- Read the workflow you are changing first, then compare it with the other files in
  `.github/workflows/` so trigger, permission, and artifact patterns stay consistent.
- Prefer the repository's Python tooling commands in `tools/` over duplicating shell
  logic inside workflows.
- Keep local workflow rules aligned with `AGENTS.md`, `.codex/rules/repo-workflow.md`,
  and the current CI shape.

## Workflow design rules

- Make the smallest correct workflow change first.
- Preserve least-privilege `permissions`. Default to `contents: read` unless a job
  truly needs more.
- Use `concurrency` on workflows or jobs where superseded runs should be canceled.
- Reuse the repository's existing setup pattern for Python, caching, and install
  steps unless the task clearly requires a different approach.
- Keep job names, step names, and artifact names plain and stable.
- Do not move repo logic into inline shell if the same logic already exists in
  `tools/`, `scripts/`, or tested commands.

## Action selection

- Follow the repo's existing convention for official GitHub actions such as
  `actions/checkout` and `actions/setup-python`.
- For third-party actions, prefer pinned versions that are already trusted in the
  repository. If you introduce a new third-party action, explain why.
- Do not add broad write permissions just to make a workflow pass.

## Before editing

Read these files when relevant:

- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.github/workflows/codeql.yml`
- `.codex/rules/repo-workflow.md`
- `.codex/rules/python-tooling.md`
- `docs/DEV.md`
- `docs/OPERATIONS.md`

## After editing

Run the repository checks that match the workflow surface you touched.

Always run:

```bash
python -m tools.format
python -m tools.lint
python -m pytest -q
```

If CI, release, packaging, or markdown validation is involved, also run the relevant
commands already used by the workflows, such as:

```bash
python -m tools.eval_groups
python -m modules.markdown_contract --root .
python -m tools.build_skill
python -m tools.build_skill --skill
```

If the workflow affects release behavior, changelog handling, or manual tagging, make
sure the release path still runs `python -m tools.lint` before artifacts are pushed.

If `actionlint` is available locally, run it after changing `.github/workflows/`.

## Change notes

- Mention trigger changes explicitly.
- Mention permission changes explicitly.
- Mention artifact, cache, or concurrency changes explicitly.
