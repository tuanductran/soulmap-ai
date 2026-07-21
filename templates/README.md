# SoulMap internal templates

This folder is internal working material. It is **not** a SoulMap skill and is
**not** included in the shipped `dist/soulmap-ai.zip` or `dist/soulmap-ai.skill`
archives. It is also not listed in `.claude-plugin/marketplace.json`.

If you are looking for the live-response templates that SoulMap actually loads at
runtime (response structure, redirects, quick reference), those moved to
[../skills/meta/response-structure.md](../skills/meta/response-structure.md),
[../skills/meta/redirect-templates.md](../skills/meta/redirect-templates.md), and
[../skills/meta/quick-reference.md](../skills/meta/quick-reference.md). Those files
are real shipped skill content and ship with the package.

Everything remaining in this folder is outward-facing product copy and internal
process material: brand copy, marketing copy, onboarding copy, founder-facing
copy, FAQ, demo scenarios, and the launch readiness checklist. Contributors use
these as reference and drafting material; they are not read by SoulMap at
runtime and are not part of the skill system.

Read [../AGENTS.md](../AGENTS.md) first so anything you draft here stays aligned
with SoulMap's core constraints, even though this folder itself is out of scope
for AGENTS.md's "shipped knowledge base" definition.

## Files in this folder

- [celebration-response.md](celebration-response.md)
- [returning-user-onboarding.md](returning-user-onboarding.md)
- [brand-copy.md](brand-copy.md)
- [marketplace-copy.md](marketplace-copy.md)
- [onboarding-copy.md](onboarding-copy.md)
- [faq.md](faq.md)
- [demo-scenarios.md](demo-scenarios.md)
- [launch-readiness-checklist.md](launch-readiness-checklist.md)
- [numerology-reflection-template.md](numerology-reflection-template.md)
- [user-charter.md](user-charter.md)
- [social-copy.md](social-copy.md)
- [email-onboarding.md](email-onboarding.md)
- [founder-copy.md](founder-copy.md)
- [founder-posts.md](founder-posts.md)

## Notes for contributors

- When a template is derived from private founder source material, keep only
  rewritten patterns and abstractions. Do not include raw excerpts, source
  names, or identifying details in tracked files.
- This folder does not need YAML front matter, since it is not a skill and is
  not subject to the skill packaging contract.
- Do not add a reference here expecting it to ship with the package. If content
  needs to be part of the shipped skill system, it belongs under `skills/`.
