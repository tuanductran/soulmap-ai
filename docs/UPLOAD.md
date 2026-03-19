# Uploading SoulMap to AI Tools

This doc explains how to use SoulMap AI by uploading either:

- The distribution archive: `dist/soulmap-ai.zip` (if your tool can read zip files)
- The source folders: `skills/` and `templates/` (upload as multiple files)

## Which file should I upload?

### Recommended: `dist/soulmap-ai.zip`

Upload `dist/soulmap-ai.zip` only if the AI tool can open or extract zip archives. If it
cannot, unzip locally and upload the `skills/` and `templates/` folders as separate
files.

## Common questions

### "What should I ask after uploading?"

Start with something explicit, for example:

- "Use this file as the governing instruction set. Follow its safety rules strictly."

### "Why is the AI not following everything?"

Most tools retrieve only relevant sections from uploaded files depending on the prompt,
and long documents may be partially used due to context limits. Try asking the tool to
quote the section it is using and to name which heading it is following.
