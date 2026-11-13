---
title: "SoulMap AI, platform integration guide"
description: "Platform deployment and migration guidance for SoulMap AI on Claude, ChatGPT, Gemini, and Poe."
doctrine_source: "SOULMAP.md"
soulmap_version: "0.14.0"
---

# SoulMap AI, platform integration guide

This file documents how to deploy SoulMap on supported AI platforms.
Platform availability, upload limits, and interface steps change independently
of SoulMap releases. The front matter declares the package compatibility and
canonical doctrine source; platform-specific facts must be checked against
current official documentation before each deployment.

**Lifecycle review date:** 2026-11-13.

## Build the distribution artifacts first

```bash
uv run soulmap build           # both artifacts
uv run soulmap dev              # verify and extract both
```

## Claude (Skills)

**Already supported.** See [../operations/UPLOAD.md](../operations/UPLOAD.md).

Upload `dist/soulmap-ai.skill` through Claude's Skills interface. If the
upload dialog requires a `.zip` extension, rename the archive without changing
its contents.

## ChatGPT (Custom GPT, legacy transition)

**Legacy platform path.**

As of 2026-11-13, new GPT creation and publishing are unavailable on personal
ChatGPT accounts (Free, Go, Plus, and Pro). Existing GPTs remain usable and may
be editable when the account, plan, and permissions allow it. New creation is
also restricted in affected managed workspaces.

OpenAI has scheduled Custom GPT retirement for **2026-12-11**. A migrated GPT
becomes read-only; its instructions and knowledge files transfer to the
replacement plugin, but its selected model and custom actions do not transfer.
Migration timing and access vary by account or workspace. Follow the in-product
notice and test the replacement before relying on it.

Official references:

- [Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)
- [Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)

### Configure an existing GPT or an eligible workspace GPT

Use these steps only when the account or workspace still has permission to
create or edit the GPT.

1. Open [Explore GPTs](https://chatgpt.com/gpts).
2. For an existing GPT, open **My GPTs** and select **Edit GPT**. For a
   workspace where new creation is still enabled, select **Create**.
3. Set the name to `SoulMap`.
4. Set the description to: `A reflective companion that helps you hear
   yourself more clearly. No prediction, no diagnosis, no dependence.`

### Paste the instructions

Copy the full text from [chatgpt-instructions.md](chatgpt-instructions.md)
into the **Instructions** field.

### Upload knowledge files

Extract `dist/soulmap-ai.zip` first, then upload the selected Markdown files
individually. OpenAI's general upload article lists up to 20 knowledge files per GPT,
while its File Uploads FAQ still lists 10. Because the official pages conflict and
Custom GPTs are retiring, verify the live builder's limit rather than relying on a
hard-coded count.

Priority files:

- [`SOULMAP.md`](../../SOULMAP.md)
- [`SKILL.md`](../../SKILL.md)
- [`skills/meta/master-prompt.md`](../../skills/meta/master-prompt.md)
- [`skills/meta/orchestration.md`](../../skills/meta/orchestration.md)
- [`skills/safety/whitelist-blacklist-system.md`](../../skills/safety/whitelist-blacklist-system.md)
- [`skills/safety/boundaries-safety.md`](../../skills/safety/boundaries-safety.md)

Optional framework files:

- [`skills/frameworks/grief-companion.md`](../../skills/frameworks/grief-companion.md)
- [`skills/frameworks/life-direction.md`](../../skills/frameworks/life-direction.md)
- [`skills/frameworks/shadow-patterns.md`](../../skills/frameworks/shadow-patterns.md)
- [`skills/frameworks/emotional-deescalation.md`](../../skills/frameworks/emotional-deescalation.md)
- [`skills/meta/deep-inquiry-bank.md`](../../skills/meta/deep-inquiry-bank.md)

### Test and share

Use Preview to test representative prompts. Sharing and publishing options
depend on account or workspace permissions. Do not assume a new personal GPT
can be created or published.

## Gemini (Gems transitioning to Skills)

**Transition begins 2026-11-17.**

Google's current transition schedule for personal Google accounts is:

- **2026-11-17:** Gems become read-only; users can no longer use, edit, or
  create them.
- **2026-12-17:** Gems are removed from Gemini Apps.
- Google says personal-account Gems and supported knowledge files will be
  automatically recreated as Skills. Personal-account Skills are available to
  users aged 18 or older.
- Work and school accounts have later transition dates: March 2027 for
  business, enterprise, and non-profit accounts; June 2027 for education.

If you still need to use a Gem on a personal account, save any knowledge files
before 2026-12-17. For ongoing use, prefer Gemini Skills rather than creating
a new Gem. The Google transition guide describes the current migration steps
and file compatibility.

Official references:

- [Use Gems in Gemini Apps](https://support.google.com/gemini/answer/15146780)
- [About the transition from Gems to skills](https://support.google.com/gemini/answer/18560919)
- [Upload and analyze files in Gemini Apps](https://support.google.com/gemini/answer/14903178)

### Create or use a Gemini Skill

For personal accounts aged 18 or older:

1. Open [Gemini](https://gemini.google.com).
2. Open **Customize**, then **Skills**. If the menu is hidden, open **More**.
3. Select **Create**, then **Create manually**.
4. Copy the SoulMap name, description, and instructions into the Skill.
5. To include supporting files, follow Google's documented download-and-
   replace workflow: download the Skill ZIP, place `SKILL.md` and supported
   knowledge files in a folder named exactly like the Skill, then use
   **Replace skill** to upload that folder.

Gemini Skills have a **100 MB total file limit**. Google currently lists
GitHub files, audio, video, legacy Office formats (`.doc`, `.xls`, `.ppt`),
and archive formats (`.zip`, `.tar`, `.7z`, `.rar`, `.gz`, `.tgz`)
as unsupported **knowledge-file sources** during the Gems-to-Skills transition.
This does not replace the separate Skill ZIP import workflow described above.
Do not assume `dist/soulmap-ai.skill` is directly compatible with Gemini Skills;
validate the artifact separately before recommending direct upload.

### Legacy Gem setup (only before the transition cutoff)

If the account still permits Gem creation before 2026-11-17:

1. Open [Gemini](https://gemini.google.com), open the sidebar, and select
   **Gems**.
2. Select **New Gem** and name it `SoulMap`.
3. Copy the text from [gemini-instructions.md](gemini-instructions.md) into
   the instructions field.
4. Under **Knowledge**, add the selected files below, then save.

Suggested initial knowledge set (not a platform file limit):

1. [`SOULMAP.md`](../../SOULMAP.md)
2. [`SKILL.md`](../../SKILL.md)
3. [`skills/meta/master-prompt.md`](../../skills/meta/master-prompt.md)
4. [`skills/meta/orchestration.md`](../../skills/meta/orchestration.md)
5. [`skills/safety/whitelist-blacklist-system.md`](../../skills/safety/whitelist-blacklist-system.md)
6. [`skills/safety/boundaries-safety.md`](../../skills/safety/boundaries-safety.md)
7. [`skills/frameworks/grief-companion.md`](../../skills/frameworks/grief-companion.md)
8. [`skills/frameworks/life-direction.md`](../../skills/frameworks/life-direction.md)
9. [`skills/frameworks/shadow-patterns.md`](../../skills/frameworks/shadow-patterns.md)
10. [`skills/meta/deep-inquiry-bank.md`](../../skills/meta/deep-inquiry-bank.md)

The 10-file limit documented by Google applies to files in a single chat
prompt; do not present it as a confirmed persistent Gem knowledge limit.
Availability and limits can vary by account and plan.

## Poe (Prompt Bot)

**Format:** System prompt, with an optional knowledge base.

### Create the bot

1. Open [Poe](https://poe.com) and select **Create bot**.
2. Choose a bot name such as `SoulMap-AI`.
3. Select a currently available base bot. Do not hard-code a model name in
   this guide because Poe's available base bots change.
4. Add the system prompt from [poe-system-prompt.md](poe-system-prompt.md).
5. Optionally add a knowledge base from supported uploaded files or text.
6. Test the bot, then choose the appropriate visibility setting.

See Poe's official [Prompt Bot creation guide](https://creator.poe.com/docs/prompt-bots/how-to-create-a-prompt-bot).

## Compatibility policy

Treat `SOULMAP.md` as the canonical doctrine and `soulmap_version` front
matter as the exact package compatibility marker. The Markdown contract checks
both; this policy defines the required human review after that static check.

| Change type | Required platform action |
| --- | --- |
| Editorial patch with no behavior, safety, upload-set, or platform-step change | Review the affected guide only; no platform redeploy is required. |
| Doctrine, safety, framework-priority, routing, or response-boundary change | Review every guide, rebuild artifacts, update all active platform deployments, and complete the manual acceptance checklist. |
| Knowledge upload-set or packaging-boundary change | Review each active platform's upload list, verify referenced files are in the standard archive, and re-upload changed knowledge to active deployments. |
| Platform UI, lifecycle, limit, or supported-file-type change | Update the affected guide, record the operational verification date, and complete the manual acceptance checklist on that platform. |
| Unsupported or behaviorally incompatible platform | Mark the deployment flow unsupported rather than weakening doctrine or claiming compatibility without evidence. |

## Updating across platforms

When a new SoulMap release ships:

1. Run `uv run soulmap build` to rebuild artifacts.
2. For ChatGPT, update only GPTs that remain editable; review migration
   requirements before the 2026-12-11 retirement date.
3. For Gemini personal accounts, update the Skill rather than the retired Gem;
   use the Google transition workflow for knowledge files.
4. For Poe, update the system prompt and optional knowledge base.
5. For Claude, re-upload the `.skill` file through the supported Skills flow.
