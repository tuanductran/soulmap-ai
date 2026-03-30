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
- preserve YAML front matter in `skills/` and `templates/`
- do not introduce Markdown structures that conflict with
  `docs/engineering/content-contract.md`
- do not use Python constant names, module paths, or code identifiers in prose
  inside `skills/` or `templates/` files, write in plain language instead

**Python identifier rule:** names like `ACUTE_GRIEF`, `VISIBILITY_FEAR_SIGNALS`, or
`src/soulmap_runtime/config/affect.py` belong in Python source files, not in Markdown knowledge
files. Readers of skill and template files are AI tools and humans, not Python
interpreters. Describe what a signal means in plain language. If a cross-reference
to the implementation is genuinely needed, use a sentence like "detected by the
grief routing layer" rather than a constant name.

## Markdownlint Compliance (`.pymarkdown.json`)

All Markdown files in this repository (including those inside `skills/` and `templates/`) must adhere to strict linting rules set in `.pymarkdown.json`. When editing or generating Markdown:

- **MD029 (Ordered list item prefix):** Always use sequential numbering for ordered lists (`1. 2. 3.`). Do NOT use the repetitive `1. 1. 1.` format.
- **MD032 (Blanks around lists):** Always surround lists (ul/ol) with blank lines.
- **MD031 (Blanks around fenced code blocks):** Always surround fenced code blocks with blank lines.
- **MD040 (Fenced code language):** Always specify a language tag for fenced code
  blocks, for example `python`, `json`, `yaml`, `text`, or `markdown`.
- **MD034 (Bare URLs):** Wrap bare URLs in angle brackets (`<http...>`) if not using link syntax.
- **Local Markdown QA:** Keep local Markdown links and canonical product/tool casing valid.
  Run `python -m soulmap_devtools.cli.check_markdown_links --root .` for broken local
  paths and anchors, and `python -m soulmap_devtools.cli.check_markdown_case --root .`
  for SoulMap-specific canonical case drift.
- **External link checks are opt-in:** When a Markdown edit changes public URLs, run
  `python -m soulmap_devtools.cli.check_markdown_links --root . --check-external`.
  This mode uses live network requests and may emit warnings for bot protection or
  rate limiting. Add `--fail-on-warning` only when you intentionally want those
  warnings to fail the command.
- **Format on Save:** Remember to always run
  `python -m soulmap_devtools.cli.format` and/or
  `python -m soulmap_devtools.cli.lint` to verify compliance after modifying
  Markdown files.
