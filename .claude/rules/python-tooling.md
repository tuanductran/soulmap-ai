---
paths:
  - modules/**/*.py
  - tools/**/*.py
  - tests/**/*.py
  - scripts/**/*.py
  - pyproject.toml
---

# Python and tooling rules

Use the repo's Python tooling contract when changing code or developer workflows.

- keep Python 3.11 compatibility
- keep `pyproject.toml` as the source of truth for Python tooling
- keep Pyright aligned with `[tool.pyright]`
- prefer typed changes that continue to pass Pyright in `standard` mode
- update tests when a tooling or contract change affects observable behavior
- prefer shared helpers in `modules/cli_payload.py` for stdin parsing, JSON error output, and common payload extraction
- prefer shared helpers in `modules/text_normalization.py` for message cleanup instead of re-implementing quote and whitespace normalization per detector
- do not create a new helper when a call site has a materially different contract or would become less clear than the local explicit code
