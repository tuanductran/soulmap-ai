---
title: "SoulMap AI, Gemini Apps Skills"
description: "Create or migrate SoulMap as a Skill in Gemini Apps, distinct from Gemini CLI local Agent Skills."
doctrine_source: "SOULMAP.md"
soulmap_version: "0.13.0"
---

# Gemini Apps Skills

**Reviewed 2026-10-10.** Google is transitioning Gemini Apps from Gems to Skills. The current official schedule is:

| Account type | Published transition date |
| --- | --- |
| Personal Google Accounts | November 2026 |
| Workspace business, enterprise, and non-profit accounts | March 2027 |
| Workspace education accounts | June 2027 |

Google says existing Gems and supported files will transition automatically when the relevant transition occurs. If you are happy to wait, you do not need to recreate an existing Gem manually. Availability and timing can differ by account type, so check the [official transition article](https://support.Google.com/gemini/answer/18560919) before changing a live setup.

## Create a SoulMap Skill

1. Build the generic package from the repository root with `uv run soulmap build`.
2. Extract `dist/soulmap-ai.zip` into a folder named `soulmap-ai`. The folder must contain the root `SKILL.md`, `SOULMAP.md`, `LICENSE`, and the `skills/` knowledge tree.
3. In Gemini Apps, open **Settings**, then **Skills**, and choose **Create manually**.
4. Create the Skill with the name `soulmap-ai`. Copy the name, description, and instructions from the canonical root `SKILL.md`. Do not create a second SoulMap entrypoint.
5. If you need the full supporting knowledge tree, use the Skill's **Skill actions** menu and **Replace skill** flow to upload the folder named `soulmap-ai`, preserving the canonical `SKILL.md` and its relative resource paths.
6. Confirm the Skill appears in Gemini Apps, then test positive and negative activation prompts plus crisis-safety precedence before relying on it.

Google's current workflow for manual migration is to create a Skill, then upload a folder with a matching name containing `SKILL.md` and any supporting files. See the [official Gemini Apps Skills transition and migration steps](https://support.Google.com/gemini/answer/18560919).

## Important compatibility boundary

- The directory layout above follows Google's documented folder-upload workflow, but SoulMap's complete package has **not** been uploaded or accepted in a live Gemini Apps account. Treat successful import and behavior as unverified until an operator completes the steps above.
- Gemini Apps Skills and Gemini CLI local Agent Skills are different product surfaces. For the CLI, use [agent-skills.md](agent-skills.md).
- Google notes that some Gems features are not yet supported by Skills. Do not assume feature parity for tools or integrations that SoulMap does not use.
- Keep the root `SKILL.md` as the only SoulMap entrypoint. Supporting files remain in the existing canonical package; no platform-specific copy of SoulMap doctrine is introduced here.
