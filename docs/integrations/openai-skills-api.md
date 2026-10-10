---
title: "SoulMap AI, OpenAI hosted Skills API"
description: "Review and manually test the SoulMap named-root Skill archive with the OpenAI Skills API."
doctrine_source: "SOULMAP.md"
soulmap_version: "0.13.0"
---

# OpenAI hosted Skills API

**Contract review date:** 2026-10-10  
**Status:** Package shape and shipped instructions reviewed; live API acceptance remains unverified.

This is the hosted OpenAI Skills API, not a ChatGPT Custom GPT and not Codex CLI's local `.agents/skills/` discovery.

## Review result

The existing `dist/soulmap-ai-claude.zip` archive uses a single top-level `soulmap-ai/` directory containing `SKILL.md` and the supporting package files. The archive excludes `.claude-plugin/` and the shipped root `SKILL.md` is now provider-neutral. The archive's local filename does not appear in its internal member paths, so a second byte-identical artifact is not justified solely to change the filename.

The `SKILL.md` frontmatter includes the required `name` and `description` plus a `version` field. The public API documentation does not establish that a live Skills API upload accepts every extra metadata field or the full SoulMap knowledge tree; the operator acceptance test must verify this.

This review confirms the repository-side package contract only. It does **not** claim that the API has accepted the archive or that a hosted model activates SoulMap correctly.

## Manual upload test

Run from the repository root. The `OPENAI_API_KEY` must be supplied securely by the operator and must never be committed or added to CI for this manual test.

```bash
uv run soulmap build --claude-ai
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY securely in your shell}"
curl --fail-with-body --location https://api.openai.com/v1/skills \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -F 'files=@./dist/soulmap-ai-claude.zip;type=application/zip'
```

Record the returned Skill ID, name, and version information without recording the API key. Use the documented list/retrieve endpoints to confirm the created Skill is visible. If upload or retrieval fails, capture the sanitized error and do not alter the canonical instructions merely to force acceptance.

## Post-upload acceptance

- Confirm the uploaded package has the intended name and exactly one root Skill manifest inside its single top-level folder.
- Confirm the supporting files are available to the host, and test the relative links from `SKILL.md`.
- Run positive reflection prompts and negative/near-miss prompts that should not activate SoulMap.
- Run crisis-safety prompts to verify safety precedence remains intact.
- Record observed behavior as product-side evidence; do not treat one successful invocation as proof of deterministic automatic activation.

Track the credentialed test in [Issue #617](https://github.com/tuanductran/soulmap-ai/issues/617).

## Official reference

OpenAI's [Skills guide](https://developers.openai.com/api/docs/guides/tools-skills) documents the hosted Skills API, directory upload, and ZIP upload form.
