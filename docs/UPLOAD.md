# Uploading SoulMap to AI Tools

## Build commands

```bash
python -m tools.build_skill           # standard zip
python -m tools.build_skill --skill   # skill package
```

## Output formats

### `dist/soulmap-ai.zip`

Standard zip archive containing `skills/`, `templates/`, root `SKILL.md`, `AGENTS.md`, and `LICENSE`.

This build intentionally excludes `.claude-plugin/`.

Use this when you want a clean knowledge archive for manual extraction, project knowledge, or document-based AI workflows.

`AGENTS.md` is intended to stand on its own in this extracted package. Do not assume repo-local workflow files are present unless they are explicitly bundled too.

### `dist/soulmap-ai.skill`

Skill-oriented archive containing the same core knowledge files as the zip build, plus the full `.claude-plugin/` directory preserved as-is.

Use this when you need to keep skill metadata bundled with the knowledge files.

Treat `.claude-plugin/` as opaque metadata during packaging and upload. Do not edit, rewrite, or flatten it as part of the build.

## AI tool compatibility

### ChatGPT

ChatGPT handles ZIP files differently depending on the context you are working in.

**Conversations (Plus/Pro with Code Interpreter enabled):** You can upload a ZIP file directly and ChatGPT will extract and read its contents using the Code Interpreter sandbox. This makes the standard `dist/soulmap-ai.zip` usable as a multi-file upload in a single step - upload the archive, then ask ChatGPT to read `SKILL.md`, `AGENTS.md`, and the relevant folders under `skills/` and `templates/`.

**Custom GPT knowledge base:** ZIP files are not supported as Custom GPT knowledge files. OpenAI's knowledge retrieval system indexes individual text-based documents (PDF, DOCX, TXT, Markdown). For a Custom GPT, extract the archive and upload the individual Markdown and text files you want indexed.

**Recommended workflow for Custom GPT:**

1. Extract `dist/soulmap-ai.zip`.
2. Upload `SKILL.md`, `AGENTS.md`, and the key files under `skills/` and `templates/`.
3. Keep each file under 512 MB and prefer plain Markdown or TXT for reliable retrieval.

### Claude

Claude handles ZIP files only via the Custom Skills feature, not as regular document uploads.

**Custom Skills (Pro, Max, Team, Enterprise - requires Code Execution enabled):** Claude's official Skills system accepts ZIP archives through `Customize > Skills > Upload a skill`. The archive must contain a `SKILL.md` at the root. The `dist/soulmap-ai.skill` file follows exactly this structure and can be uploaded directly - rename it to `.zip` first if the upload dialog requires a `.zip` extension.

**Claude.ai conversations and Project knowledge:** ZIP files are not supported as regular uploads. Claude accepts PDF, DOCX, TXT, RTF, HTML, CSV, Markdown, and images up to 30 MB per file. For Project knowledge, upload the individual extracted files.

**Recommended workflow for Claude Projects:**

1. Extract `dist/soulmap-ai.zip`.
2. Upload `SKILL.md`, `AGENTS.md`, and the relevant files under `skills/` and `templates/` to the Project knowledge base.
3. For the full Custom Skills experience, upload `dist/soulmap-ai.skill` (or rename to `.zip`) via `Customize > Skills`.

### Any Agent Skills-compatible agent

Agent Skills are an open format built around a portable skill folder with `SKILL.md` at the root. The `.skill` archive is a transport package that can be unpacked into that directory structure on any compatible agent runtime.

## Standard build examples

### Zip build for ChatGPT (Code Interpreter) or multi-file tools

Build the standard zip:

```bash
python -m tools.build_skill
```

What you get:

* `dist/soulmap-ai.zip`
* no `.claude-plugin/`

Suggested use for ChatGPT with Code Interpreter:

1. Upload `dist/soulmap-ai.zip` directly in a ChatGPT Plus/Pro conversation.
2. Ask ChatGPT to extract the archive and load `SKILL.md` and `AGENTS.md` as the governing instruction set.

Suggested use for Custom GPT knowledge or Claude Projects:

1. Extract the zip.
2. Upload the Markdown or text files that match your tool's supported file types.
3. Point the tool at `SKILL.md`, `AGENTS.md`, and the relevant folders under `skills/` and `templates/`.

### Skill build for Claude Custom Skills or skill-oriented agents

Build the skill package:

```bash
python -m tools.build_skill --skill
```

What you get:

* `dist/soulmap-ai.skill`
* `.claude-plugin/` preserved

Suggested use for Claude Custom Skills:

1. Go to `Customize > Skills` in Claude.ai (requires Pro, Max, Team, or Enterprise with Code Execution enabled).
2. Click `+` then `Upload a skill`.
3. Upload `dist/soulmap-ai.skill` directly (or rename to `.zip` if the dialog requires it).
4. Keep `.claude-plugin/` unchanged inside the archive.

Suggested use for other skill-oriented agents:

1. If your tool expects a directory-based skill install, unpack the archive first.
2. If your tool accepts packaged skills directly, upload the `.skill` file without modifying its internal paths.

## Common questions

### "What should I ask after uploading?"

Start with something explicit, for example:

* "Use this file as the governing instruction set. Follow its safety rules strictly."

### "Why is the AI not following everything?"

Most tools retrieve only relevant sections from uploaded files depending on the prompt, and long documents may be partially used due to context limits. Try asking the tool to quote the section it is using and to name which heading it is following.
