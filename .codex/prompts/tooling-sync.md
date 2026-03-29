# Tooling Sync Prompt

Use this prompt for Python tooling and root-config synchronization passes in SoulMap AI.

- Start from `pyproject.toml`, root dotfiles, `tools/`, `scripts/`, and `docs/DEV.md`.
- Treat `pyproject.toml` and Python entry points in `tools/` as the source of truth.
- Keep shell wrappers thin and make root config match actual repo behavior.
- Audit dependency bots, pre-commit hooks, markdown tooling, and local build commands together.
- Remove stale config and duplicated logic rather than layering on more wrappers.
- Run format, lint, pytest, and the relevant build or eval commands after meaningful edits.
