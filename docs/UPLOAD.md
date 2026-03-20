# Uploading SoulMap to AI Tools

## Build commands

```bash
python -m tools.build_skill_zip           # zip only (default)
python -m tools.build_skill_zip --zip     # zip only (explicit)
python -m tools.build_skill_zip --skill   # .skill only
python -m tools.build_skill_zip --all     # both zip and .skill
```

## Output formats

### `dist/soulmap-ai.zip`

Standard zip archive containing `skills/`, `templates/`, `AGENTS.md`,
`LICENSE`, and `.claude-plugin/marketplace.json`.

Use for Claude plugin marketplace or when extracting files manually.

### `dist/soulmap-ai.skill`

Agent Skills-compliant archive (zip with `.skill` extension).

Upload directly to AI tools via their skill/plugin settings:

- **Claude.ai** - Settings > Features > Upload Custom Skill
- **GitHub Copilot** - VS Code skill settings
- **OpenAI Codex** - `.codex/skills/` or API upload

The `.skill` file includes a root-level `SKILL.md` entry-point manifest
so the AI tool can discover and activate the skill by name and description,
and load the right knowledge files on demand.

## Common questions

### "What should I ask after uploading?"

Start with something explicit, for example:

- "Use this file as the governing instruction set. Follow its safety rules strictly."

### "Why is the AI not following everything?"

Most tools retrieve only relevant sections from uploaded files depending on the prompt,
and long documents may be partially used due to context limits. Try asking the tool to
quote the section it is using and to name which heading it is following.
