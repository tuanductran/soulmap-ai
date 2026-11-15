# Claude Plugin Metadata

This directory contains metadata used by the Claude plugin distribution.

## Included metadata

- `marketplace.json` provides marketplace metadata for the plugin package.

## Packaging boundaries

- `marketplace.json` is included in `dist/soulmap-ai.skill`.
- This README is repository-only and excluded from both distribution archives.
- The standard `dist/soulmap-ai.zip` archive does not include `.claude-plugin/`.
- Keep product doctrine and user-facing frameworks in the root `SOULMAP.md` and
  `skills/` files.
- Do not add user-facing knowledge or implementation instructions to plugin metadata.
- Validate packaging changes with the standard build and extracted-artifact
  verification workflow.
