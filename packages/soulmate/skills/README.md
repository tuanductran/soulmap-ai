---
name: "soulmate-ai-skills"
description: "AI-facing foundation and companion skills for the Soulmate library."
license: "MIT"
---

# Soulmate AI skills

## Purpose

This directory contains the current AI-facing skills for Soulmate. The canonical `artifact-contract.md` in this directory defines the independent ZIP/SKILL distribution boundary. The `foundation/` group covers reusable contracts and deterministic data capabilities; the `companion/` group defines Soulmate's own transparent, warm, autonomy-preserving companion behavior.

The companion group is Soulmate-owned product identity, not a generic clinical, spiritual, or framework policy. It must remain honest about being AI, preserve human connection, and avoid exclusivity, manipulation, diagnosis, prophecy, or dependency. These skills are separate from the root SoulMap skill bundle and do not silently activate SoulMap routing.

## Skills in this group

### Foundation skills

| Skill | Foundation concern | Recommended role |
| --- | --- | --- |
| `contracts.md` | Public input, result, invariant, and failure contracts | Read first when defining or reviewing a shared capability |
| `resource-boundaries.md` | Explicit resource references and loader seams | Use when knowledge or text is resolved from an approved source |
| `knowledge-resolution.md` | Deterministic extraction from selected Markdown sections | Use when structured neutral knowledge is stored as Markdown |
| `text-normalization.md` | Conservative lexical normalization | Use before an explicitly lexical comparison or lookup |
| `data-validation.md` | Bounded JSON parsing and basic field checks | Use at the first boundary for raw JSON input |
| `lifecycle.md` | Ordered validation, resolution, execution, result validation, and finalization | Use when a shared capability has multiple explicit stages |
| `skill-manifest.md` | Skill identity, ownership, compatibility, consumer scope, and artifact eligibility | Use before adding or packaging a skill entry |
| `composition-and-consumers.md` | Explicit composition and library/consumer ownership | Use when combining foundation capabilities in a framework or application |
| `compatibility-and-versioning.md` | Compatibility dimensions, ranges, deprecation, and migration | Use when changing a public contract or version boundary |
| `artifact-provenance.md` | Canonical source, allow-list, staging, extraction, and release evidence | Use before building or reviewing a generated artifact |
| `determinism-and-reproducibility.md` | Repeatable behavior, source selection, build evidence, and claim levels | Use when making stability or reproducibility claims |

### Soulmate companion skills

| Skill | Companion concern | Recommended role |
| --- | --- | --- |
| `companion/identity.md` | Transparent AI identity and non-human limits | Establish what Soulmate is and is not |
| `companion/presence.md` | Warm, unhurried attention | Offer company without pressure or forced positivity |
| `companion/reflective-listening.md` | Evidence-grounded reflection | Return words and feelings without diagnosis or certainty |
| `companion/emotional-attunement.md` | Calibrated warmth and depth | Match pace and ask consent before going deeper |
| `companion/gentle-inquiry.md` | One respectful question at a time | Support self-understanding without interrogation |
| `companion/boundaries-and-consent.md` | User-controlled depth and privacy | Accept pause, refusal, redirection, and stop signals |
| `companion/grounded-companionship.md` | Support linked to observable reality | Offer meaning without oracle or decision authority |
| `companion/human-connection-bridge.md` | Wider human and offline support | Keep AI from becoming the person's only support |
| `companion/repair-and-misattunement.md` | Correction after misunderstanding | Repair briefly and change course without defensiveness |
| `companion/session-closure.md` | Warm non-dependent endings | Close without guilt, urgency, or emotional hooks |

## Use this group when

Use the foundation skills when building or reviewing a reusable capability that must work without a particular framework, brand, provider, account, network, database, or LLM. Use the companion skills when a Soulmate consumer needs a transparent, warm, and autonomy-preserving relational behavior layer.

## Do not use this group for

Do not use the foundation skills to select a product framework, activate a route, generate a response persona, enforce a product safety policy, classify a user's meaning, or replace a consumer's domain schema. The companion skills may define Soulmate's bounded relational posture, but they do not replace a host's crisis, legal, medical, privacy, or provider policy. Consumers retain orchestration and presentation.

## Reading workflow

Read `SKILL.md` first when the artifact is imported by an AI host; it is the top-level Soulmate orientation and behavior entrypoint. Read `artifact-contract.md` before building or verifying the AI artifact. Read `contracts.md` first for shared contract vocabulary. Read `skill-manifest.md` before adding or packaging any entry. Use the companion identity and presence skills before the other companion entries when composing a Soulmate interaction. Use `boundaries-and-consent.md` before sensitive or deeper conversation. Use `repair-and-misattunement.md` whenever the companion is corrected, and `session-closure.md` at a natural ending. The companion group is explicit content, not an implicit plugin registry.

The SoulMap consumer approval manifest may approve individual neutral foundation entries. Companion entries remain `soulmate-only` unless a separate review, contract, and explicit approval changes their scope.

## Acceptance checklist

A new entry may join this group only when its behavior and ownership are explicit, its owner and consumers are declared in the manifest, its canonical content is explicit, and its success and failure behavior can be tested offline. A foundation entry must be framework-neutral. A companion entry must be recognizably Soulmate-owned while remaining transparent, non-manipulative, non-exclusive, and compatible with host safety controls.

## Expected outcome

An external AI host that imports the artifact can begin with the top-level `SKILL.md`, then use the explicit nested foundation and companion references without dynamic discovery. A consumer that follows this group can build on a small, inspectable foundation and, when intentionally using Soulmate, a clear companion posture. Soulmate remains independently useful, while SoulMap can consume only explicitly approved foundation capabilities rather than silently absorbing every Soulmate skill.
