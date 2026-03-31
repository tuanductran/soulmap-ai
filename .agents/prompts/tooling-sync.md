# Tooling sync prompt

Use this prompt for Python tooling and root-config synchronization passes in SoulMap AI.

- Start from `pyproject.toml`, root dotfiles, `src/soulmap_devtools/`, `scripts/`,
  and `docs/engineering/DEV.md`.
- Treat `pyproject.toml` and Python entry points in `src/soulmap_devtools/` as the
  source of truth.
- Keep shell wrappers thin and make root config match actual repo behavior.
- Audit dependency bots, Git hooks, Markdown tooling, and local build commands together.
- Remove stale config and duplicated logic rather than layering on more wrappers.
- Run format, lint, pytest, and the relevant build or eval commands after meaningful edits.
