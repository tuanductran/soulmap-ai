---
paths:
  - '**/*.md'
  - .pymarkdown.json
  - lefthook.yml
  - pyproject.toml
---

# Markdown portability rules

Keep Markdown compatible across AI tools and OS editors.

- use `'` and `"` instead of smart quotes
- use `-` instead of em dashes
- use `...` instead of ellipsis
- preserve YAML front matter in `skills/` (required); `templates/` is internal-only
  and does not require front matter
- do not introduce Markdown structures that conflict with
  `docs/engineering/content-contract.md`
- do not use Python constant names, module paths, or code identifiers in prose
  inside `skills/` or `templates/` files, write in plain language instead
- do not reference a repository-only path from `skills/` content, since `skills/`
  ships standalone and the reference will resolve to nothing once extracted

**Python identifier rule:** names like `ACUTE_GRIEF`, `VISIBILITY_FEAR_SIGNALS`, or
`src/soulmap/runtime/config/safety.py` belong in Python source files, not in Markdown knowledge
files. Readers of skill and template files are AI tools and humans, not Python
interpreters. Describe what a signal means in plain language. If a cross-reference
to the implementation is genuinely needed, use a sentence like "detected by the
grief routing layer" rather than a constant name.

**Shipped-package boundary rule:** `skills/` content ships standalone inside
`dist/soulmap-ai.zip` and `dist/soulmap-ai.skill`. Neither archive includes `docs/`,
`tests/`, `.claude/`, `.github/`, `scripts/`, `library/`, `src/soulmap/`,
`pyproject.toml`, `uv.lock`, or any other repository-only path (see
`docs/engineering/repo-contract.md`'s packaged-contents row for the exact list). A
reference from `skills/` content to one of those paths resolves to nothing once the
archive is extracted, even when it is a plain mention rather than a clickable
Markdown link. Before adding a cross-reference inside `skills/`, check whether the
target actually ships in the same archive. If it does not, state the underlying fact
directly instead of pointing to the file, or link to another `skills/` file that
already covers it.
`tests/contract/test_epistemic_guardrail_boundary_contract.py::test_shipped_skills_do_not_reference_repository_only_surfaces`
enforces this at CI time, but treat it as a safety net, not a substitute for checking
before you write the reference: its forbidden-path list is necessarily finite, and a
past gap in that list (a narrower pattern than the one now in place) let one
reference through undetected.

## Markdownlint Compliance (`.pymarkdown.json`)

All Markdown files in this repository (including those inside `skills/` and `templates/`) must adhere to strict linting rules set in `.pymarkdown.json`. When editing or generating Markdown:

- **MD029 (Ordered list item prefix):** Always use sequential numbering for ordered lists (`1. 2. 3.`). Do NOT use the repetitive `1. 1. 1.` format.
- **MD032 (Blanks around lists):** Always surround lists (ul/ol) with blank lines.
- **MD031 (Blanks around fenced code blocks):** Always surround fenced code blocks with blank lines.
- **MD040 (Fenced code language):** Always specify a language tag for fenced code
  blocks, for example `python`, `json`, `yaml`, `text`, or `markdown`.
- **MD034 (Bare URLs):** Wrap bare URLs in angle brackets (`<http...>`) if not using link syntax.
- **Local Markdown QA:** Keep local Markdown links and canonical product/tool casing valid.
  Run `uv run soulmap check-links --root .` for broken local
  paths and anchors, and `uv run soulmap check-case --root .`
  for SoulMap-specific canonical case drift.
- **External link checks are opt-in:** When a Markdown edit changes public URLs, run
  `uv run soulmap check-links --root . --check-external`.
  This mode uses live network requests and may emit warnings for bot protection or
  rate limiting. Add `--fail-on-warning` only when you intentionally want those
  warnings to fail the command.
- **Format on Save:** Remember to always run
  `uv run soulmap format` and/or
  `uv run soulmap lint` to verify compliance after modifying
  Markdown files.
