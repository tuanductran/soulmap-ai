# Claude Skill Distribution Contracts

**Research date:** 2026-10-10

SoulMap is Claude-first, but its Claude distribution targets are not interchangeable. Keep the existing single canonical root `SKILL.md` and knowledge tree; build target-specific archives from the same source files.

## Verified platform requirements

### Claude.ai Custom Skills

Anthropic's Help Center says the ZIP must contain the Skill directory as its root, named to match the Skill, with `SKILL.md` and supporting resources inside. A ZIP with files directly at archive root is explicitly documented as incorrect.

Source: Anthropic Help Center, "How to create custom skills" (`https://support.claude.com/en/articles/12512198-how-to-create-custom-skills`).

The existing `dist/soulmap-ai.zip` contract places `SKILL.md`, `SOULMAP.md`, `LICENSE`, and `skills/` directly at archive root, so it remains the generic/manual-extraction artifact. Issue [#605](https://github.com/tuanductran/soulmap-ai/issues/605) adds the separate `dist/soulmap-ai-claude.zip` with a `soulmap-ai/` prefix for the documented Claude.ai upload layout.

### Claude Code Skills and plugins

Claude Code filesystem Skills use a directory containing `SKILL.md`; project Skills are typically located under `.claude/skills/`. Plugins are a separate distribution layer that can bundle Skills and other extension components and use plugin/marketplace metadata.

Sources:

- Claude Code extension overview (`https://code.claude.com/docs/en/features-overview`)
- Agent Skills overview (`https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`)

The repository's `dist/soulmap-ai.skill` currently preserves `.claude-plugin/marketplace.json`. Do not infer that this artifact is a valid Claude.ai Custom Skills ZIP solely because it is a ZIP-compatible archive, or that a generic Skill ZIP is an installable Claude Code plugin.

## Artifact boundaries in this repository

- `dist/soulmap-ai.zip`: existing generic/manual-extraction artifact; root-level file contract remains unchanged.
- `dist/soulmap-ai.skill`: existing plugin-metadata-preserving artifact; its contract remains unchanged.
- `dist/soulmap-ai-claude.zip`: dedicated Claude.ai upload artifact with every shipped member under `soulmap-ai/`; repository validation is implemented, but live-upload acceptance has not been tested.

## Validation boundary

Repository tests can verify archive paths, manifest metadata, content integrity, and Markdown links. They cannot prove that a live Claude.ai upload or a Claude Code marketplace installation is accepted by the platform. Record live acceptance only after testing in the intended product surface.

No SoulMap doctrine, routing, detector, runtime, or safety semantics are defined by this distribution note.
