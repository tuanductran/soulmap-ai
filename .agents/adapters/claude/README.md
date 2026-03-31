# Claude adapter

This adapter holds Claude-specific local configuration that cannot live in the shared
portable layer unchanged.

## What belongs here

- Claude settings files
- Claude-only adapter notes
- file-path glue required by Claude entrypoints

## What does not belong here

- shared repo rules
- shared maintenance skills
- shared prompts
- SoulMap doctrine or shipped product knowledge

The shared source of truth remains [`.agents/`](../../).
