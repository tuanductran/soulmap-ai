---
title: "SoulMap AI, Claude integration guide"
description: "Claude Code plugin manifest, Claude.ai Custom Skills packaging, and Claude deployment guidance."
doctrine_source: "SOULMAP.md"
soulmap_version: "0.15.1"
---

# Claude integration guide

Claude is the primary integration target for SoulMap. This guide covers the Claude Code plugin, Claude.ai Custom Skills, and the distinction between those packaging formats.

The behavioral source of truth remains **SOULMAP.md** and the supporting Markdown under **skills/**. Platform metadata describes how Claude discovers the Skill; it must not duplicate product doctrine.

## Build the artifacts

~~~bash
uv run soulmap build
uv run soulmap dev --once
~~~

The build produces:

- **dist/soulmap-ai.skill** — Claude Code plugin-aware archive. It contains the canonical knowledge files plus **.claude-plugin/plugin.json** and the Git marketplace catalog.
- **dist/soulmap-ai.zip** — portable knowledge archive. It contains **SKILL.md**, **SOULMAP.md**, **LICENSE**, and the supporting **skills/** directory, without Claude-specific plugin metadata.

## Claude Code plugin

### Plugin layout

The Claude Code plugin root has this layout:

~~~text
soulmap-ai/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── SKILL.md
├── SOULMAP.md
├── LICENSE
└── skills/
    ├── frameworks/
    ├── meta/
    ├── safety/
    ├── voice/
    └── ...
~~~

Claude Code reads the plugin manifest from **.claude-plugin/plugin.json**. Other component directories belong beside **.claude-plugin/** at the plugin root, not inside it.

### Manifest fields used by SoulMap

The manifest follows Anthropic's [plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference).

| Field | Purpose in this plugin |
| --- | --- |
| **$schema** | Editor autocomplete and JSON validation using the published Claude Code plugin manifest schema. Claude Code ignores this field at runtime. |
| **name** | Stable kebab-case identifier: **soulmap-ai**. |
| **displayName** | Human-readable product name: **SoulMap AI**. |
| **version** | Must match the repository release version. |
| **description** | Short discovery description, not a replacement for the Skill instructions. |
| **author** | Maintainer name and public contact/profile details. |
| **homepage**, **repository** | Canonical documentation and source locations. |
| **license** | SPDX license identifier: **MIT**. |
| **keywords** | Search and discovery terms. |
| **skills** | Explicitly includes the repository root with **["./"]**, where the single canonical **SKILL.md** lives. |

The root Skill points to the supporting Markdown in **skills/**. Those files are knowledge resources, not separate plugin Skills. Keep exactly one shipped Skill entrypoint.

The manifest is optional in Claude Code generally, but SoulMap keeps it explicit so plugin identity, version, metadata, and root Skill discovery are machine-readable. Only **name** is required by the manifest schema; the additional fields above are intentional project metadata.

### Validate and test

Run the authoritative Claude Code manifest validator:

~~~bash
claude plugin validate . --strict
~~~

Then load the repository as a local plugin for a smoke test:

~~~bash
claude --plugin-dir .
~~~

Test representative prompts and confirm the root Skill can load the linked doctrine and supporting knowledge. The CLI validator checks the manifest and component paths; it does not replace the repository's own tests, safety evaluations, packaging checks, or a live behavior review.

### Marketplace and directory publishing

The Git marketplace catalog remains available in **.claude-plugin/marketplace.json** for repository-based Claude Code distribution. Public community submission is a separate review process; follow the current [Claude Code plugin sharing and submission guide](https://code.claude.com/docs/en/plugins). Anthropic lists a [Claude.ai submission form](https://claude.ai/admin-settings/directory/submissions/plugins/new) for eligible Team/Enterprise organizations and an [Anthropic Console form](https://platform.claude.com/plugins/submit) for individual authors.

## Claude.ai Custom Skills

Claude.ai Custom Skills use a different upload wrapper from the Claude Code plugin archive. The custom Skill ZIP must contain a named folder at its root and a lowercase **skill.md** file inside that folder.

1. Build the standard archive using **uv run soulmap build**.
2. Extract **dist/soulmap-ai.zip** into a staging directory named **soulmap-ai/**.
3. In that staging copy only, rename **SKILL.md** to **skill.md**. Do not rename the canonical repository file.
4. ZIP the **soulmap-ai/** folder itself so it is the single top-level entry in the resulting archive.
5. In Claude, open **Customize → Skills → + → Create skill → Upload a skill**, upload the ZIP, enable the Skill, and test it with representative prompts.

Do not upload **dist/soulmap-ai.skill** as a Claude.ai Custom Skills ZIP. That archive preserves Claude Code plugin metadata and has files at its archive root; it is not the named-folder wrapper required by Claude.ai.

Official references: [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) and [Use Skills in Claude](https://support.claude.com/en/articles/12512180).

## Claude API

Claude API Skills are a separate integration surface from Claude.ai Custom Skills and Claude Code plugins. Follow the current [Claude API Skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide) for its API upload contract; do not assume that a Claude.ai ZIP or a Claude Code plugin archive can be submitted unchanged.

## Packaging and release rules

- Keep **SKILL.md** as the canonical root entrypoint in the repository.
- Keep all product doctrine and knowledge in Markdown. The Python layer builds, validates, and packages; it does not replace the knowledge source.
- Keep plugin metadata under **.claude-plugin/** and plugin components at the plugin root.
- Keep the version in **plugin.json**, **marketplace.json**, **SKILL.md**, **pyproject.toml**, and this guide synchronized.
- Verify both archives, their exact member sets, extracted contents, and SHA-256 integrity before release.

For the canonical repository packaging boundary and release workflow, see [UPLOAD.md](../operations/UPLOAD.md) and the [repository contract](../engineering/repo-contract.md).
