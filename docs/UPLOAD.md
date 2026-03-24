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

**ChatGPT:** ChatGPT's official docs describe uploads for common file types and project reference material such as PDFs, spreadsheets, docs, images, and pasted text. They do not explicitly document `.zip` or `.skill` as first-class upload formats, so the safest workflow is to extract the archive first and upload the Markdown or text files you want it to use.

**Claude:** Claude's official upload docs cover standard document types, and Anthropic's Skills docs describe custom Skills as ZIP-based packages containing a `SKILL.md` file. For Claude, use the extracted knowledge files for normal document uploads, and use a ZIP-based skill package only in workflows that explicitly support Claude Skills.

**Any Agent Skills-compatible agent:** Agent Skills are an open format built around a portable skill folder with `SKILL.md` at the root, so the `.skill` archive should be treated as a transport package that can be unpacked into that directory structure.

## Standard build examples

### Zip example for ChatGPT or document-based tools

Build the standard zip:

```bash
python -m tools.build_skill
```

What you get:

* `dist/soulmap-ai.zip`
* no `.claude-plugin/`

Suggested use:

1. Extract the zip.
2. Upload the Markdown or text files that match your tool's supported file types.
3. Point the tool at `SKILL.md`, `AGENTS.md`, and the relevant folders under `skills/` and `templates/`.

### Skill example for skill-oriented tools

Build the skill package:

```bash
python -m tools.build_skill --skill
```

What you get:

* `dist/soulmap-ai.skill`
* `.claude-plugin/` preserved

Suggested use:

1. Keep `.claude-plugin/` unchanged.
2. If your tool expects a directory-based skill install, unpack the archive first.
3. If your tool accepts packaged skills directly, upload the `.skill` file without modifying its internal paths.

## Common questions

### "What should I ask after uploading?"

Start with something explicit, for example:

* "Use this file as the governing instruction set. Follow its safety rules strictly."

### "Why is the AI not following everything?"

Most tools retrieve only relevant sections from uploaded files depending on the prompt, and long documents may be partially used due to context limits. Try asking the tool to quote the section it is using and to name which heading it is following.
