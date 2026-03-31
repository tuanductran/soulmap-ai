# Docs skills templates sync prompt

Use this prompt when you need to verify that `docs/`, `skills/`, and `templates/`
still describe one coherent SoulMap package.

- Read `AGENTS.md` first.
- Read `docs/engineering/repo-contract.md`, `docs/engineering/content-contract.md`,
  and `docs/README.md`.
- Read the relevant `SKILL.md` files under `skills/` and `templates/`.
- Audit for:
  - missing file references
  - orphaned docs or weakly surfaced docs
  - template or skill files omitted from their nearest index
  - docs that mention shipped surfaces inaccurately
  - package instructions that no longer match the real file graph
  - tracked Markdown that leaks local paths, source-specific names, or temporary
    working markers
- Prefer the smallest correct fix.
- If a file exists but is intentionally leaf-level, do not force extra references.
- If a file is a real entry point or guide and is missing from navigation, fix the
  nearest index file.
- Run `python -m soulmap_runtime.guards.markdown_contract --root .` and
  `python -m soulmap_devtools.cli.format` after meaningful edits.
