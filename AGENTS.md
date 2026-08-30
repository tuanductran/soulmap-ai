# AGENTS.md

Baseline contract for AI coding agents working in the `soulmap-ai` repository.
`CLAUDE.md` is a symlink to this file, so Claude Code reads the same contract as
any other agent.

This file is about the repository and how to work in it. For SoulMap's own
product doctrine, safety rules, and response behavior, read
[SOULMAP.md](SOULMAP.md) first, before touching anything under `skills/` or the
runtime safety modules.

## What this repository is

SoulMap AI is a content-first reflective-companion product: a Markdown knowledge
base under `skills/`, plus a small, deterministic Python routing and safety layer
under `src/soulmap/runtime/`, plus a maintainer tooling package under
`src/soulmap/devtools/`. See [README.md](README.md) for the product framing.

## Where things live

- `SOULMAP.md`, the shipped SoulMap doctrine, safety rules, and framework hierarchy
- `skills/`, the shipped knowledge base (frameworks, safety, brand, voice, meta,
  spiritual)
- `templates/`, internal-only product and brand copy, not shipped
- `src/soulmap/runtime/`, the executable routing, detection, and safety-guard layer
- `src/soulmap/devtools/`, the maintainer CLI (`soulmap ...`), eval runners, and
  packaging tools
- `tests/`, the pytest suite; `evals/datasets/`, source-backed routing and safety
  evals
- `docs/`, contributor, tester, operator, and architecture documentation
- `.claude/`, the local Claude-specific workflow layer, see
  [.claude/README.md](.claude/README.md)

Full structural contract, including what ships and how each surface is validated:
[docs/engineering/repo-contract.md](docs/engineering/repo-contract.md).

## Setup

```bash
uv python install 3.11
bash scripts/bootstrap_venv.sh
```

This repo standardizes on Python 3.11 and `uv` for local development and CI.
Activating `.venv` is optional when using `uv run ...`. Full setup notes:
[CONTRIBUTING.md](CONTRIBUTING.md).

## Format, lint, and test

```bash
uv run soulmap format
uv run soulmap lint
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap test -n auto -q
uv run python tests/eval_regression/test_safety_evals.py
```

Before pushing, run at minimum:

```bash
uv run soulmap lint --skip-tests
uv run soulmap test -n auto -q
```

If a change touches `src/soulmap/runtime/`, also run the full test suite and the
safety evals above. If a change touches `skills/` or `templates/`, also run
`markdown-contract`. If a change touches `CHANGELOG.md`, root Markdown, or
`docs/`, also run `lint`.

## Build artifacts

```bash
uv run soulmap build          # dist/soulmap-ai.zip
uv run soulmap build --skill  # dist/soulmap-ai.skill
```

Run these after any change under `skills/` to confirm the new content packages
correctly. See [docs/operations/UPLOAD.md](docs/operations/UPLOAD.md).

## Git workflow

- `main` is protected. Never push directly to it.
- One branch per logical change, named by type: `feat/...`, `fix/...`,
  `chore/...`, `docs/...`, `test/...`, `ci/...`.
- Conventional Commits: `<type>(<scope>): <summary>`.
- Push the branch, open a PR, merge, then delete the branch.

Full rules: [.claude/rules/git-and-release.md](.claude/rules/git-and-release.md).

## Working rules

- Prefer the smallest correct change. Do not fix unrelated things in the same
  diff.
- Prefer updating an existing file over creating a parallel one.
- Content changes (frameworks, safety language, brand copy) belong in `skills/`
  or `templates/`, not in Python. Python is orchestration, detection, and
  enforcement only; see
  [docs/engineering/known-limitations.md](docs/engineering/known-limitations.md).
- Do not duplicate a rule that already lives in `SOULMAP.md` or
  `docs/engineering/repo-contract.md`; link to it instead.
- Keep Python typed: Ruff enforces Google-style docstrings and full annotations,
  and Pyright runs in standard mode. See
  [.claude/rules/python-tooling.md](.claude/rules/python-tooling.md).
- Before editing `.github/workflows/`, read
  [.claude/rules/github-actions.md](.claude/rules/github-actions.md).

## Safety-sensitive surfaces

Changes under `src/soulmap/runtime/detectors/`, `src/soulmap/runtime/guards/`, or
`src/soulmap/runtime/routing/` are safety-adjacent. Read `SOULMAP.md`'s
non-negotiable safety rules and
[docs/engineering/safety-enforcement-matrix.md](docs/engineering/safety-enforcement-matrix.md)
first, and run the full test and safety-eval commands above before pushing.

## Local Claude workflow layer

`.claude/` holds Claude-specific supplemental workflow support: path-scoped rules
in `.claude/rules/`, repeatable maintainer skills in `.claude/skills/`, and
reusable prompts in `.claude/prompts/`. Start from
[.claude/prompts/project-operating-prompt.md](.claude/prompts/project-operating-prompt.md)
for broad maintainer work. This layer is local-only, not part of the shipped
package, and subordinate to this file and to `SOULMAP.md`. See
[.claude/README.md](.claude/README.md).
