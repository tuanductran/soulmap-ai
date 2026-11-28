# Claude Code Plugin Metadata

This directory contains the metadata Claude Code reads for the SoulMap plugin.

## Files

- **plugin.json** is the plugin manifest. It defines the canonical plugin identity, release metadata, discovery information, and the root Skill location.
- **marketplace.json** is the Git-based marketplace catalog retained for repository-based Claude Code distribution compatibility.

The canonical manifest reference is the [Claude Code plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference).

## Manifest contract

- The manifest lives at **.claude-plugin/plugin.json**.
- The plugin identifier is **soulmap-ai**; **displayName** is the user-facing label.
- The single shipped Skill entrypoint is the repository-root **SKILL.md**. The manifest explicitly declares **skills: ["./"]** so Claude Code scans the plugin root for that entrypoint.
- Supporting reflective knowledge remains in the root **skills/** directory. These Markdown files are resources referenced by the root Skill, not independent Skill entrypoints.
- The manifest is metadata only. Product doctrine and behavioral guidance stay in **SOULMAP.md** and **skills/**.

## Distribution boundary

- Both **plugin.json** and **marketplace.json** are included in **dist/soulmap-ai.skill**.
- The standard **dist/soulmap-ai.zip** excludes **.claude-plugin/** and remains the platform-neutral Markdown knowledge archive.
- This README is repository-only and excluded from both archives.
- Do not move plugin components such as **skills/**, **commands/**, or **hooks/** inside **.claude-plugin/**. The directory is for plugin metadata; components live at the plugin root.
- Validate the plugin with **claude plugin validate . --strict** from the repository root, then run the repository build and extracted-artifact verification workflow.

The Git marketplace catalog supports repository-based Claude Code distribution. Public community submission is a separate review process; follow the current [Claude Code plugin submission guide](https://code.claude.com/docs/en/plugins) and use the [Claude.ai submission form](https://claude.ai/admin-settings/directory/submissions/plugins/new) or [Anthropic Console form](https://platform.claude.com/plugins/submit), as appropriate for the publishing account.
