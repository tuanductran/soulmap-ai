---
title: "SoulMap AI, platform integration guide"
description: "Deployment and local Agent Skills guidance for ChatGPT, Gemini Apps and CLI, Poe, Claude, Codex, and GitHub Copilot."
doctrine_source: "SOULMAP.md"
soulmap_version: "0.13.0"
---

# SoulMap AI, platform integration guide

This file documents how to deploy SoulMap on each supported AI platform.
Each platform requires different files and setup steps. The front matter declares
its exact package compatibility and canonical doctrine source; all platform guides
must be reviewed when that version changes.

## Build the distribution artifacts first

```bash
uv run soulmap build               # dist/soulmap-ai.zip
uv run soulmap build --skill       # dist/soulmap-ai.skill
uv run soulmap build --claude-ai   # dist/soulmap-ai-claude.zip
```

## Local Agent Skills (Codex CLI, Gemini CLI, GitHub Copilot CLI)

**Format:** Extracted folder containing the single root `SKILL.md` and the shipped knowledge tree.

See [agent-skills.md](agent-skills.md) for the installation commands and per-tool discovery checks. This documents local skill discovery only; it does not claim hosted upload or live activation acceptance.

## OpenAI Skills API (hosted)

**Format:** A ZIP containing one top-level Skill folder with `SKILL.md` and supporting resources.

See [openai-skills-api.md](openai-skills-api.md) for the compatibility review and credentialed manual test procedure. The package shape is reviewed, but live API acceptance and activation remain unverified.

## Claude (Skills)

**Already supported.** See [../operations/UPLOAD.md](../operations/UPLOAD.md).

Upload `dist/soulmap-ai-claude.zip` via `Customize`, then `Skills`, then `Upload a skill`.
This archive uses the documented named-root layout; live upload acceptance has not yet
been verified.

## ChatGPT (Custom GPT)

**Format:** Instructions text + individual `.md` knowledge files (ZIP not supported).

### Step 1, confirm eligibility and open the GPT editor

**Reviewed 2026-10-10.** OpenAI's current help documentation says new GPT creation and publishing are available to eligible Business, Enterprise, and Edu workspace users with the required permissions. Personal Free, Go, Plus, and Pro accounts cannot create or publish new GPTs; editing an existing GPT depends on the account and permission conditions.

1. Open [Explore GPTs](https://chatgpt.com/gpts) or [the GPT editor](https://chatgpt.com/create).
2. Continue only if the account or workspace exposes the Create/configuration workflow.
3. Name: `SoulMap`
4. Description: `A reflective companion that helps you hear yourself more clearly.
   No prediction, no diagnosis, no dependence.`

See the [official GPT creation and editing guide](https://help.OpenAI.com/en/articles/8554397-gpts) for current eligibility and UI details.

### Step 2, paste the instructions

Copy the full text from [chatgpt-instructions.md](chatgpt-instructions.md)
and paste it into the **Instructions** field.

### Step 3, upload knowledge files

Extract `dist/soulmap-ai.zip` first, then upload the selected Markdown files individually. Put behavioral rules and tone in the GPT's **Instructions** field; use Knowledge files as reference material.

Start with the priority files below, then add optional references only as the current editor's file limit permits. OpenAI's help pages have described different limits in different upload contexts, so this guide intentionally does not promise a fixed count; follow the limit shown in the current GPT editor.

Priority files:

- [`../SOULMAP.md`](../../SOULMAP.md)
- [`../SKILL.md`](../../SKILL.md)
- [`../skills/meta/master-prompt.md`](../../skills/meta/master-prompt.md)
- [`../skills/meta/orchestration.md`](../../skills/meta/orchestration.md)
- [`../skills/safety/whitelist-blacklist-system.md`](../../skills/safety/whitelist-blacklist-system.md)
- [`../skills/safety/boundaries-safety.md`](../../skills/safety/boundaries-safety.md)

Optional references:

- [`../skills/frameworks/grief-companion/content/grief-companion.md`](../../skills/frameworks/grief-companion/content/grief-companion.md)
- [`../skills/frameworks/life-direction/content/life-direction.md`](../../skills/frameworks/life-direction/content/life-direction.md)
- [`../skills/frameworks/shadow-patterns/content/shadow-patterns.md`](../../skills/frameworks/shadow-patterns/content/shadow-patterns.md)
- [`../skills/frameworks/emotional-deescalation.md`](../../skills/frameworks/emotional-deescalation.md)
- [`../skills/meta/deep-inquiry-bank.md`](../../skills/meta/deep-inquiry-bank.md)

### Step 4, set conversation starters

Copy from [chatgpt-instructions.md](chatgpt-instructions.md)
under the `## Conversation starters` section.

### Step 5, save or publish if eligible

Sharing and publishing options depend on the account, workspace, and permissions. Personal accounts currently cannot publish newly created GPTs; use the options actually available in the current editor and consult OpenAI's official guide before treating this as a deployable path.

## Gemini Apps (Gems; legacy workflow)

**Status:** Gemini Apps is transitioning from Gems to Skills. This section is retained only for accounts where the existing Gems workflow remains available; use the [Gemini Apps Skills guide](gemini-apps-skills.md) for the current direction.

**Reviewed 2026-10-10.** Google's official transition schedule says personal Google Accounts move in November 2026, Workspace business/enterprise/non-profit accounts in March 2027, and Workspace education accounts in June 2027. Google says existing Gems and supported files will transition automatically. Check the [official Gems-to-Skills transition article](https://support.Google.com/gemini/answer/18560919) for current account-specific details.

If you still need to configure a legacy Gem, the previous instructions and knowledge-file shortlist remain below. Do not treat the old file-count limit or UI labels as current guarantees.

### Legacy setup: create or edit a Gem

1. Open [Gemini Apps](https://gemini.google.com) and use the Gems area only if it remains available for your account.
2. Copy the instructions from [gemini-instructions.md](gemini-instructions.md) into the Gem's Instructions field.
3. If the editor permits Knowledge files, start with the priority sources below and follow the current UI's file and size limits.

Priority sources:

1. [`../SOULMAP.md`](../../SOULMAP.md)
2. [`../SKILL.md`](../../SKILL.md)
3. [`../skills/meta/master-prompt.md`](../../skills/meta/master-prompt.md)
4. [`../skills/meta/orchestration.md`](../../skills/meta/orchestration.md)
5. [`../skills/safety/whitelist-blacklist-system.md`](../../skills/safety/whitelist-blacklist-system.md)
6. [`../skills/safety/boundaries-safety.md`](../../skills/safety/boundaries-safety.md)
7. [`../skills/frameworks/grief-companion/content/grief-companion.md`](../../skills/frameworks/grief-companion/content/grief-companion.md)
8. [`../skills/frameworks/life-direction/content/life-direction.md`](../../skills/frameworks/life-direction/content/life-direction.md)
9. [`../skills/frameworks/shadow-patterns/content/shadow-patterns.md`](../../skills/frameworks/shadow-patterns/content/shadow-patterns.md)
10. [`../skills/meta/deep-inquiry-bank.md`](../../skills/meta/deep-inquiry-bank.md)

## Poe (Bot)

**Format:** System prompt for a prompt bot. API bots are a separate integration path.

**Reviewed 2026-10-10.** Poe's available bot types and underlying models change over time. Choose from the current Create Bot interface rather than relying on a hard-coded model name. See the [official Poe FAQ](https://help.Poe.com/hc/en-us/articles/19944206309524-Poe-FAQs).

### Step 1, create the bot

1. Go to [poe.com](https://poe.com)
2. Click **Create bot**
3. Name: `SoulMap-AI`
4. Choose a currently available text model from Poe's Create Bot interface. Model availability changes over time; this guide does not guarantee that any named model remains selectable.

### Step 2, paste the system prompt

Copy the full text from [poe-system-prompt.md](poe-system-prompt.md)
and paste it into the **System prompt** field.

### Step 3, set the intro message

Copy from [poe-system-prompt.md](poe-system-prompt.md) under
`## Intro message`.

### Step 4, publish

Set visibility to **Public** to allow discovery.

## Compatibility policy

Treat `SOULMAP.md` as the canonical doctrine and `soulmap_version` front matter
as the exact package compatibility marker. The Markdown contract checks both;
this policy defines the required human review after a change passes that static
check.

| Change type | Required platform action |
| --- | --- |
| Editorial patch with no behavior, safety, upload-set, or platform-step change | Review the affected guide only; no platform redeploy is required. |
| Doctrine, safety, framework-priority, routing, or response-boundary change | Review every guide, rebuild artifacts, update all active platform deployments, and complete the manual acceptance checklist. |
| Knowledge upload-set or packaging-boundary change | Review the ChatGPT and Gemini upload lists, verify referenced files are in the standard archive, and re-upload changed knowledge to active deployments. |
| Platform UI, limit, or supported-file-type change | Update the affected guide, record the operational verification date, and complete the manual acceptance checklist on that platform. |
| Unsupported or behaviorally incompatible platform | Mark the deployment flow unsupported rather than weakening doctrine or claiming compatibility without evidence. |

## Updating across platforms

When a new SoulMap release ships:

1. Run `uv run soulmap build` to rebuild artifacts
2. Update ChatGPT GPT: re-upload changed knowledge files, update instructions if changed
3. Update Gemini Gem: re-upload changed files
4. Update Poe bot: paste updated system prompt
5. Claude skill: re-upload `.skill` file
