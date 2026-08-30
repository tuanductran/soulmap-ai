# Docs skills templates sync prompt

Use this prompt when you need to verify that `docs/` and `skills/` (the shipped
package) still describe one coherent SoulMap package, and that internal-only
`templates/` content stays consistent with it.

- Read `SOULMAP.md` first.
- Read `docs/engineering/repo-contract.md`, `docs/engineering/content-contract.md`,
  and `docs/README.md`.
- Read the relevant `SKILL.md` files under `skills/` and `templates/README.md`.
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
- Run `uv run soulmap markdown-contract --root .` and
  `uv run soulmap format` after meaningful edits.
