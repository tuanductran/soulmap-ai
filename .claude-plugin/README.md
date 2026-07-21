# Claude Plugin Metadata

This folder contains local Claude skill-package metadata preserved in
`dist/soulmap-ai.skill`.

## Current role

- `marketplace.json`, grouped marketplace-style skill metadata for the `.skill` package

## Important boundaries

- This folder is not part of the standard `dist/soulmap-ai.zip` archive.
- Treat this folder as packaging metadata, not as shipped SoulMap doctrine.
- Do not move product truth here. Keep doctrine and frameworks in the root package
  files under `AGENTS.md` and `skills/`. `templates/` is internal-only and is not
  part of the shipped package.
- When editing this folder, verify that `python -m tools.build_skill --skill` still
  preserves it as-is.
