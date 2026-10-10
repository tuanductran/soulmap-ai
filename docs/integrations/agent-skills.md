---
title: "SoulMap AI, portable local Agent Skills"
description: "Install the existing SoulMap knowledge package as a local skill in Codex CLI, Gemini CLI, or GitHub Copilot CLI."
doctrine_source: "SOULMAP.md"
soulmap_version: "0.13.0"
---

# Portable local Agent Skills

This guide covers **local folder-based Skill discovery** in Codex CLI, Gemini CLI, and GitHub Copilot CLI. It does not claim that a hosted upload, marketplace listing, or live activation has been tested.

The supported source artifact is the existing generic archive, `dist/soulmap-ai.zip`. It contains the single root `SKILL.md`, `SOULMAP.md`, `LICENSE`, and the shipped `skills/` knowledge tree. Keep those files together: the root Skill uses relative links to the canonical knowledge resources.

## 1. Build and extract the package

From the SoulMap repository root:

```bash
uv run soulmap build
mkdir -p "$HOME/.agents/skills/soulmap-ai"
unzip -o dist/soulmap-ai.zip -d "$HOME/.agents/skills/soulmap-ai"
```

This installs a personal copy shared across compatible tools. For a repository-local install, use the workspace path instead:

```bash
mkdir -p .agents/skills/soulmap-ai
unzip -o dist/soulmap-ai.zip -d .agents/skills/soulmap-ai
```

After extraction, verify that `SKILL.md` is directly inside `soulmap-ai/`, not nested in another directory:

```text
.agents/skills/soulmap-ai/
├── SKILL.md
├── SOULMAP.md
├── LICENSE
└── skills/
```

Do not copy the repository's local `.claude/` maintainer configuration into a user's Skill directory. It is not part of the shipped archive and is not required by the portable Skill.

## 2. Codex CLI

Codex discovers local skills under `.agents/skills/`, including the repository root or the user's `$HOME/.agents/skills/` directory.

1. Run Codex from the repository where the workspace Skill was installed, or use the personal install above.
2. Run `/skills` to inspect available skills.
3. Explicitly invoke the Skill with `$soulmap-ai` in a prompt when you want to test selection directly.
4. If the Skill does not appear, restart Codex and inspect the extracted path and frontmatter.

Official documentation: https://developers.openai.com/codex/skills

## 3. Gemini CLI

Gemini CLI discovers skills from `~/.agents/skills/` and the workspace `.agents/skills/` alias, as well as its native `.gemini/skills/` directories.

1. Extract the package to one of the `.agents/skills/soulmap-ai/` paths above.
2. Run `gemini skills list` or use `/skills list` in an interactive session.
3. If the Skill was added during a session, run `/skills reload` and confirm `soulmap-ai` appears.

Official documentation: https://geminicli.com/docs/cli/skills/

## 4. GitHub Copilot CLI

Copilot CLI supports project skills under `.agents/skills/` and personal skills under `~/.agents/skills/`.

1. Extract the package to one of those paths.
2. Run `copilot skill list` or `/skills list` in an interactive session.
3. Use `/soulmap-ai` to request the Skill explicitly, or inspect it with the CLI's skill information commands if discovery fails.

Official documentation: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills

## Compatibility boundary

- This guide documents supported discovery paths and package layout from the vendors' public documentation; it is not a live compatibility certification.
- Automatic activation depends on each host's model and discovery behavior. A visible Skill listing does not prove correct behavior on every prompt.
- Keep the root `SKILL.md` as the sole SoulMap entrypoint. Files below `skills/` are supporting canonical knowledge, not additional Skills.
- The generic archive is for local extraction. The Claude.ai named-root archive and the OpenAI hosted Skills API have separate distribution contracts; do not infer acceptance from the local ZIP structure.
- ChatGPT Custom GPT, Gemini Gems, and Poe setup instructions remain in the existing [platform integration guide](README.md). Those surfaces use their own configuration workflows and are not the same as local Agent Skills.
