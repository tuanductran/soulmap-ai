---
paths:
  - '**/*'
---

# Git and release rules

Use Conventional Commits:

`<type>(<scope>): <summary>`

Recommended types:

- `feat`
- `fix`
- `chore`
- `docs`
- `refactor`
- `test`
- `build`
- `ci`
- `perf`
- `revert`

Examples:

- `feat(detectors): add spiritual bypass signal`
- `fix(packaging): prevent heading collisions in AGENTS bundle`
- `docs(brand): clarify surfaces and scope`
- `chore: update dev tooling`

Preferred branch names:

- `feat/...`
- `fix/...`
- `chore/...`
- `docs/...`
- `test/...`
- `ci/...`

## Branch workflow (required)

Never push directly to `main`. All changes must go through a branch and PR.

### Standard flow

```bash
# 1. Always start from an up-to-date main
git checkout main
git pull origin main

# 2. Create a branch named after the change type
git checkout -b fix/crisis-hotlines

# 3. Make changes and commit with Conventional Commits
git add <files>
git commit -m "fix(safety): embed crisis hotlines in response_guidance"

# 4. Push the branch (never main)
git push origin fix/crisis-hotlines

# 5. Open a PR on GitHub for review before merging
```

### Rules

- `main` is the protected branch, no direct pushes
- One branch per logical change, do not mix unrelated fixes
- Branch name must match the commit type prefix
- Delete the branch after the PR is merged
- If a change touches `src/soulmap_runtime/`, run `python -m pytest -n auto -q` before pushing
- If a change touches `skills/` or `templates/`, run `python -m soulmap_runtime.guards.markdown_contract --root .` before pushing
- If a change touches `CHANGELOG.md`, root Markdown, or `docs/*.md`, run `python -m soulmap_devtools.cli.lint` before pushing or tagging a release
- Before any manual release or tag push, run `python -m soulmap_devtools.cli.format`, `python -m soulmap_devtools.cli.lint`, and `python -m pytest -n auto -q`

### Branch naming examples

| Change | Branch name |
| :--- | :--- |
| Fix crisis detector hotlines | `fix/crisis-hotlines` |
| Add new shadow pattern | `feat/shadow-spiritual-bypass` |
| Update CHANGELOG | `docs/changelog-update` |
| Add CI safety eval step | `ci/safety-evals-workflow` |
| Add T008 red-team case | `test/t008-red-team` |
| Bump dev dependencies | `chore/bump-dev-deps` |
