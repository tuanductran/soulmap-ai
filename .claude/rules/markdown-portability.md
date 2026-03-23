---
paths:
  - '**/*.md'
  - .pymarkdown.json
  - .pre-commit-config.yaml
  - pyproject.toml
---

# Markdown Portability Rules

Keep Markdown compatible across AI tools and OS editors.

- use `'` and `"` instead of smart quotes
- use `-` instead of em dashes
- use `...` instead of ellipsis
- preserve YAML front matter in `skills/` and `templates/`
- do not introduce Markdown structures that conflict with `docs/content-contract.md`
- do not use Python constant names, module paths, or code identifiers in prose
  inside `skills/` or `templates/` files - write in plain language instead

**Python identifier rule:** names like `ACUTE_GRIEF`, `VISIBILITY_FEAR_SIGNALS`, or
`modules/config/affect.py` belong in Python source files, not in Markdown knowledge
files. Readers of skill and template files are AI tools and humans, not Python
interpreters. Describe what a signal means in plain language. If a cross-reference
to the implementation is genuinely needed, use a sentence like "detected by the
grief routing layer" rather than a constant name.
