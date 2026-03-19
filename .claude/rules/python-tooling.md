---
paths:
  - modules/**/*.py
  - tools/**/*.py
  - tests/**/*.py
  - scripts/**/*.py
  - pyproject.toml
---

# Python And Tooling Rules

Use the repo's Python tooling contract when changing code or developer workflows.

- keep Python 3.11 compatibility
- keep `pyproject.toml` as the source of truth for Python tooling
- keep Pyright aligned with `[tool.pyright]`
- prefer typed changes that continue to pass Pyright in `standard` mode
- update tests when a tooling or contract change affects observable behavior
