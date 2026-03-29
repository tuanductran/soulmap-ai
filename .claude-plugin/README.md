# Claude Plugin Metadata

This folder contains local Claude skill-package metadata preserved in
`dist/soulmap-ai.skill`.

## Current role

- `marketplace.json`, grouped marketplace-style skill metadata for the `.skill` package

## Important boundaries

- This folder is not part of the standard `dist/soulmap-ai.zip` archive.
- Treat this folder as packaging metadata, not as shipped SoulMap doctrine.
- Do not move product truth here. Keep doctrine, frameworks, safety, and templates in
  the root package files under `AGENTS.md`, `skills/`, and `templates/`.
- When editing this folder, verify that `python -m tools.build_skill --skill` still
  preserves it as-is.
