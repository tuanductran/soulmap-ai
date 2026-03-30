# Content graph audit prompt

Use this prompt for a focused audit of `docs/`, `skills/`, and `templates/` as one
connected knowledge graph.

- Start from `AGENTS.md`, `docs/engineering/repo-contract.md`, `docs/engineering/content-contract.md`, and
  `README.md`.
- Treat `skills/` and `templates/` as shipped source of truth.
- Treat `docs/` as the explanation and operating layer around those shipped surfaces.
- Check for:
  - forgotten or weakly surfaced files
  - stale internal links
  - SKILL indexes that omit real files
  - docs that fail to route readers to existing surfaces
  - templates or skills that exist but are not discoverable from the right entry points
- Prefer updating existing indexes and guide files before creating new docs.
- Do not invent new product surfaces just to make the graph feel fuller.
- Keep fixes structural and navigational unless a real content contradiction is found.
- Run `python -m soulmap_runtime.guards.markdown_contract --root .` after meaningful edits.
