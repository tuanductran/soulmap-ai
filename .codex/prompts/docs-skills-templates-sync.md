# Docs Skills Templates Sync Prompt

Use this prompt when you need to verify that `docs/`, `skills/`, and `templates/`
still describe one coherent SoulMap package.

- Read `AGENTS.md` first.
- Read `docs/repo-contract.md`, `docs/content-contract.md`, and `docs/README.md`.
- Read the relevant `SKILL.md` files under `skills/` and `templates/`.
- Audit for:
  - missing file references
  - orphaned docs or weakly surfaced docs
  - template or skill files omitted from their nearest index
  - docs that mention shipped surfaces inaccurately
  - package instructions that no longer match the real file graph
- Prefer the smallest correct fix.
- If a file exists but is intentionally leaf-level, do not force extra references.
- If a file is a real entry point or guide and is missing from navigation, fix the
  nearest index file.
- Run `python -m modules.markdown_contract --root .` and `python -m tools.format` after
  meaningful edits.
