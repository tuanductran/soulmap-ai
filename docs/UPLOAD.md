# Uploading SoulMap to AI Tools

This doc explains how to use SoulMap AI by uploading either:

- The single-file bundle: `skills/AGENTS.md` (recommended for most tools)
- The distribution archive: `dist/soulmap-ai.zip` (only if your tool can read zip files)

## Which file should I upload?

### Recommended: `skills/AGENTS.md`

Upload `skills/AGENTS.md` when you want one file that contains the full knowledge base
and is easy for AI tools to read.

### Optional: `dist/soulmap-ai.zip`

Upload `dist/soulmap-ai.zip` only if the AI tool can open or extract zip archives. If it
cannot, unzip locally and upload `skills/AGENTS.md` instead.

## ChatGPT (chatgpt.com)

### Upload to a chat

Use the attachment (add) button in the chat composer to upload `skills/AGENTS.md`, then
ask ChatGPT to follow it as the primary instruction set.

If you have uploaded the file previously, you can add it from your Library via the
composer menu.

### Add as "Knowledge" to a custom GPT

If you are building a custom GPT, you can attach files as Knowledge in the GPT editor.
Knowledge files are chunked and stored for retrieval during chats.

Notes:

- File size limits and context limits apply to uploads.
- Files uploaded to chats vs Knowledge can behave differently depending on product
  settings and plan.

## Claude (claude.ai)

### Upload to a chat

Claude supports uploading documents in chats (for example: PDF, DOCX, CSV, TXT, JSON).
Per-file size limits and per-chat file count limits may apply depending on plan.

### Add to a Project knowledge base

If you use Projects, you can upload the file into the project knowledge base so it's
available across chats within that project.

## Gemini (Gemini apps)

### Add files as knowledge for a Gem

Gemini supports adding files under a Gem's Knowledge section (upload from device or from
Google Drive).

## Common questions

### "What should I ask after uploading?"

Start with something explicit, for example:

- "Use this file as the governing instruction set. Follow its safety rules strictly."
- "Answer in English only. Use the selected framework exactly as written."

### "Why is the AI not following everything?"

Most tools retrieve only relevant sections from uploaded files depending on the prompt,
and long documents may be partially used due to context limits. Try asking the tool to
quote the section it is using and to name which heading it is following.
