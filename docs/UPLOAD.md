# Uploading SoulMap to AI Tools

## Build commands

```bash
python -m tools.build_skill           # standard zip
python -m tools.build_skill --skill   # skill package
```

## Output formats

### `dist/soulmap-ai.zip`

Standard zip archive containing `skills/`, `templates/`, root `SKILL.md`,
`AGENTS.md`, and `LICENSE`.

This build intentionally excludes `.claude-plugin/`.

Use this when you want a clean knowledge archive for manual extraction, project
knowledge, or document-based AI workflows.

### `dist/soulmap-ai.skill`

Skill-oriented archive containing the same core knowledge files as the zip build,
plus the full `.claude-plugin/` directory preserved as-is.

Use this when you need to keep skill metadata bundled with the knowledge files.

Treat `.claude-plugin/` as opaque metadata during packaging and upload. Do not edit,
rewrite, or flatten it as part of the build.

## AI tool compatibility

Compatibility notes reviewed against official product docs and official project pages:

- **ChatGPT**: supports common uploaded document types for knowledge and chats, but the
  official Help Center does not document `.zip` or `.skill` as first-class upload
  types. Use `dist/soulmap-ai.zip` as a distribution archive, extract it, then upload
  the Markdown or text files you need.
- **Claude**: official upload docs list document uploads such as PDF, DOCX, TXT, HTML,
  JSON, and more, but do not document `.zip` or `.skill` as a first-class upload type.
  Anthropic also publicly describes Agent Skills as a Claude capability. In practice,
  use the extracted knowledge files for document uploads, and use `dist/soulmap-ai.skill`
  only where your Claude workflow explicitly accepts a skill package.
- **Claude Code**: Agent Skills is an Anthropic open standard. Install skills
  from the marketplace with `/plugin install` or add a local skill directory.
  Use `dist/soulmap-ai.skill` as a transport archive and unpack it into your
  skill directory, or reference the source `skills/` folder directly.
- **Any Agent Skills-compatible agent**: The `.skill` format follows the open
  standard at agentskills.io. Unpack the archive to get the skill directory and
  place `SKILL.md` at its root.

Official references:

- Agent Skills open standard: <https://agentskills.io/home>
- Agent Skills specification: <https://github.com/agentskills/agentskills>
- Anthropic Agent Skills overview: <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- Anthropic Agent Skills docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
- Anthropic skills repository: <https://github.com/anthropics/skills>
- ChatGPT file uploads: <https://help.openai.com/en/articles/8983675-what-types-of-files-are-supported>
- Claude file uploads: <https://support.claude.com/en/articles/8241126-uploading-files-to-claude>

## Standard build examples

### Zip example for ChatGPT or document-based tools

Build the standard zip:

```bash
python -m tools.build_skill
```

What you get:

- `dist/soulmap-ai.zip`
- no `.claude-plugin/`

Suggested use:

1. Extract the zip.
2. Upload the Markdown or text files that match your tool's supported file types.
3. Point the tool at `SKILL.md`, `AGENTS.md`, and the relevant folders under `skills/`
   and `templates/`.

### Skill example for skill-oriented tools

Build the skill package:

```bash
python -m tools.build_skill --skill
```

What you get:

- `dist/soulmap-ai.skill`
- `.claude-plugin/` preserved

Suggested use:

1. Keep `.claude-plugin/` unchanged.
2. If your tool expects a directory-based skill install, unpack the archive first.
3. If your tool accepts packaged skills directly, upload the `.skill` file without
   modifying its internal paths.

## Common questions

### "What should I ask after uploading?"

Start with something explicit, for example:

- "Use this file as the governing instruction set. Follow its safety rules strictly."

### "Why is the AI not following everything?"

Most tools retrieve only relevant sections from uploaded files depending on the prompt,
and long documents may be partially used due to context limits. Try asking the tool to
quote the section it is using and to name which heading it is following.
