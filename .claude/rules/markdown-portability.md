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
