# Codex Python Tooling

Use the repo's Python tooling contract when changing code or developer workflows.

- keep Python 3.11 compatibility
- keep `pyproject.toml` as the source of truth for Python tooling
- keep Pyright aligned with repo configuration
- prefer typed changes that continue to pass local checks
- update tests when a tooling or contract change affects observable behavior
- prefer shared helpers in `modules/cli_payload.py` for stdin parsing, JSON error output, and common payload extraction
- prefer shared helpers in `modules/text_normalization.py` for repeated message normalization logic
- keep explicit local code when a module has a different payload contract and a shared helper would hide that difference
