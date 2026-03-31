---
paths:
  - '**/*'
---

# Repository workflow rules

Use these rules for repository-wide working discipline.

## Sources of truth

- Treat `AGENTS.md` as the baseline SoulMap doctrine, safety contract, and shipped
  package guidance.
- Treat `docs/engineering/repo-contract.md` as the repository structure contract.
- Treat `docs/engineering/maintenance-boundary.md` as the scope-control document.
- Treat `docs/engineering/content-contract.md` as the Markdown structure contract.
- Treat `language-and-grammar.md` as the repo-local prose style rule.
- Prefer existing repo files over generic assumptions.

## Working style

- Make the smallest correct change first.
- Do not add new surfaces, modules, or docs unless there is a current need.
- Prefer updating existing files over creating parallel ones.
- Keep repo language plain, specific, and ASCII-safe in Markdown.
- Ensure all Markdown updates comply strictly with `.pymarkdown.json` rules, for
  example `MD032` padding around lists and `MD040` fenced code languages.

## Before editing

- Read the nearest source-of-truth file first.
- Check the root `../skills/` directory for a matching skill first.
- Do not change behavior, packaging, or docs by inference alone when the repo already
  defines the contract elsewhere.

## After editing

Run these checks after meaningful changes:

```bash
python -m soulmap_devtools.cli.format
python -m soulmap_runtime.guards.markdown_contract --root .
python -m soulmap_devtools.cli.check_markdown_links --root .
python -m soulmap_devtools.cli.check_markdown_case --root .
python -m soulmap_devtools.cli.lint
python -m pytest -n auto -q
```

If the change edits public URLs in Markdown, also run:

```bash
python -m soulmap_devtools.cli.check_markdown_links --root . --check-external
```

Keep this external mode opt-in. It depends on live network responses and should not be
treated as the default fast local gate.

Before pushing, keep the local CI mirror green:

```bash
python -m soulmap_devtools.cli.lint --skip-tests
python -m pytest -n auto -q
```

Do not rely on `git push` hooks for this repo. Run those commands explicitly before
pushing when the change is meaningful or touches tested/runtime surfaces.

If packaging or release behavior changed, also run:

```bash
python -m soulmap_devtools.cli.build_skill
python -m soulmap_devtools.cli.build_skill --skill
```

## AI tool guardrails

- Do not widen scope just because a change is possible.
- Do not invent product capabilities the repo does not implement.
- Do not add dependency-inviting copy, advice-like language, or unsupported claims.
- Do not leave generated caches or build artifacts in the working tree unless they are
  intentionally part of the task.
