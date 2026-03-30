---
paths:
  - src/**/*.py
  - tests/**/*.py
  - scripts/**/*.py
  - pyproject.toml
---

# Python and tooling rules

Use the repo's Python tooling contract when changing code or developer workflows.

- keep Python 3.11 compatibility
- keep `pyproject.toml` as the source of truth for Python tooling
- prefer Ruff as the single Python lint, format, and import-sorting tool unless the
  repo has a proven gap it cannot cover
- keep Pyright aligned with `[tool.pyright]`
- prefer typed changes that continue to pass Pyright in `standard` mode
- update tests when a tooling or contract change affects observable behavior
- prefer shared helpers in `src/soulmap_runtime/io/cli_payload.py` for stdin parsing, JSON error output, and common payload extraction
- prefer shared helpers in `src/soulmap_runtime/io/text_normalization.py` for message cleanup instead of re-implementing quote and whitespace normalization per detector
- prefer package-first commands rooted in `src/soulmap_devtools/` and `src/soulmap_runtime/`
- keep `.venv` editable install aligned with `scripts/bootstrap_venv.sh` and `pyproject.toml`
- if subprocess tests need repo-local imports, pass `PYTHONPATH=src` explicitly rather than reviving root-level shim packages
- for pure helpers such as text normalization, JSON parsing, and small contract utilities, prefer adding compact property-based tests when that catches more edge cases than example-only tests
- do not create a new helper when a call site has a materially different contract or would become less clear than the local explicit code
