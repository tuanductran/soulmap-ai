---
title: "SoulMap AI - Platform Integration Guide"
description: "Step-by-step instructions for deploying SoulMap AI on ChatGPT, Gemini, Poe, and Claude."
---

# SoulMap AI - Platform Integration Guide

This file documents how to deploy SoulMap AI on each supported AI platform.
Each platform requires different files and setup steps.

## Build the distribution artifacts first

```bash
python -m tools.build_skill           # dist/soulmap-ai.zip
python -m tools.build_skill --skill   # dist/soulmap-ai.skill
```

---

## Claude (Skills)

**Already supported.** See [docs/UPLOAD.md](UPLOAD.md).

Upload `dist/soulmap-ai.skill` (rename to `.zip` if the dialog requires it) via:
`Customize > Skills > Upload a skill`

---

## ChatGPT (Custom GPT)

**Format:** Instructions text + individual `.md` knowledge files (ZIP not supported).

### Step 1 - Create the GPT

1. Go to [chatgpt.com/create](https://chatgpt.com/create)
2. Click **Configure** (not Create)
3. Name: `SoulMap AI`
4. Description: `A reflective companion that helps you hear yourself more clearly.
   No prediction, no diagnosis, no dependence.`

### Step 2 - Paste the instructions

Copy the full text from [docs/integrations/chatgpt-instructions.md](integrations/chatgpt-instructions.md)
and paste it into the **Instructions** field.

### Step 3 - Upload knowledge files

Upload these files from `dist/soulmap-ai.zip` (extract first):

Priority files (upload these):
- `AGENTS.md`
- `SKILL.md`
- `skills/meta/master-prompt.md`
- `skills/meta/orchestration.md`
- `skills/safety/whitelist-blacklist-system.md`
- `skills/safety/boundaries-safety.md`

Optional (for richer framework access):
- `skills/frameworks/grief-companion.md`
- `skills/frameworks/life-direction.md`
- `skills/frameworks/shadow-patterns.md`
- `skills/frameworks/emotional-deescalation.md`
- `skills/meta/deep-inquiry-bank.md`

### Step 4 - Set conversation starters

Copy from [docs/integrations/chatgpt-instructions.md](integrations/chatgpt-instructions.md)
under the `## Conversation starters` section.

### Step 5 - Publish

Set sharing to **Anyone with the link** for private use, or **Public** for GPT Store.

---

## Gemini (Gems)

**Format:** Instructions text + up to 10 uploaded files.

### Step 1 - Create the Gem

1. Go to [gemini.google.com](https://gemini.google.com)
2. Click **Gem manager** in the left sidebar
3. Click **New Gem**
4. Name: `SoulMap AI`

### Step 2 - Paste the instructions

Copy the full text from [docs/integrations/gemini-instructions.md](integrations/gemini-instructions.md)
and paste it into the instructions field.

### Step 3 - Upload knowledge files (max 10)

Upload these files (extract from `dist/soulmap-ai.zip` first):

1. `AGENTS.md`
2. `SKILL.md`
3. `skills/meta/master-prompt.md`
4. `skills/meta/orchestration.md`
5. `skills/safety/whitelist-blacklist-system.md`
6. `skills/safety/boundaries-safety.md`
7. `skills/frameworks/grief-companion.md`
8. `skills/frameworks/life-direction.md`
9. `skills/frameworks/shadow-patterns.md`
10. `skills/meta/deep-inquiry-bank.md`

### Step 4 - Share

Click **Save**, then click the **Share** icon in Gem manager to generate a share link.

---

## Poe (Bot)

**Format:** System prompt only (no file upload for standard bots).

### Step 1 - Create the bot

1. Go to [poe.com](https://poe.com)
2. Click **Create bot**
3. Name: `SoulMap-AI`
4. Base model: `Claude-3.5-Sonnet` or `GPT-4o`

### Step 2 - Paste the system prompt

Copy the full text from [docs/integrations/poe-system-prompt.md](integrations/poe-system-prompt.md)
and paste it into the **System prompt** field.

### Step 3 - Set the intro message

Copy from `poe-system-prompt.md` under `## Intro message`.

### Step 4 - Publish

Set visibility to **Public** to allow discovery.

---

## Updating across platforms

When a new SoulMap release ships:

1. Run `python -m tools.build_skill` to rebuild artifacts
2. Update ChatGPT GPT: re-upload changed knowledge files, update instructions if changed
3. Update Gemini Gem: re-upload changed files
4. Update Poe bot: paste updated system prompt
5. Claude skill: re-upload `.skill` file
