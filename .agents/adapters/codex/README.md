# Codex adapter

This adapter documents Codex-specific local wiring for the shared `.agents/` layer.

Codex currently uses:

- [`.codex/`](../../../.codex/) as the visible entry layer
- [`.github/hooks/codex-local.json`](../../../.github/hooks/codex-local.json) for
  hook wiring
- shared rules, skills, prompts, and hooks from [`.agents/`](../../)

## What belongs here

- Codex-specific adapter notes
- any future Codex-only metadata that cannot stay portable

## What does not belong here

- duplicated repo rules
- duplicated skills or prompts
- SoulMap doctrine or shipped product knowledge
