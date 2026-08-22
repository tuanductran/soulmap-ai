---
name: "soulmate-foundation-skills"
description: "Framework-neutral AI-facing foundation skills for the Soulmate library."
license: "MIT"
---

# Soulmate foundation skills

## Purpose

This directory contains the current AI-facing foundation skills for Soulmate. The canonical `artifact-contract.md` in this directory defines the independent ZIP/SKILL distribution boundary. The initial P0 set covers reusable contracts and deterministic data capabilities; the P1 and P2 additions cover lifecycle, manifest, composition, compatibility, provenance, and reproducibility without importing SoulMap's doctrine, routing policy, safety posture, voice, brand, or spiritual frameworks.

These skills are written for a future Soulmate skill artifact. They are not part of the root SoulMap skill bundle, and they do not instruct a consuming framework how to behave as a product.

## Skills in this group

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
| `artifact-contract.md` | Canonical file set, formats, allow-list, provenance, integrity, and release boundary | Read before building or verifying the AI artifact |

## Use this group when

Use these skills when building or reviewing a reusable foundation capability that must work without a particular framework, brand, provider, account, network, database, or LLM. Apply the relevant skill before a consumer-specific policy or presentation layer.

## Do not use this group for

Do not use these skills to select a product framework, activate a route, generate a response persona, enforce a product safety policy, classify a user's meaning, or replace a consumer's domain schema. The foundation explains contracts and mechanics; consumers retain policy, interpretation, and presentation.

## Reading workflow

Read `artifact-contract.md` before building or verifying the AI artifact. Read `contracts.md` first to establish the shared contract vocabulary. Then read `skill-manifest.md` before adding or packaging an entry, and use `lifecycle.md` when the capability has multiple explicit stages. Use `composition-and-consumers.md` when a framework combines foundation operations, `compatibility-and-versioning.md` when a public boundary changes, `artifact-provenance.md` before generating an artifact, and `determinism-and-reproducibility.md` when making repeatability claims. A resource-backed Markdown capability will normally use `resource-boundaries.md` followed by `knowledge-resolution.md`. A raw JSON capability will use `data-validation.md`. A lexical lookup may use `text-normalization.md`, while retaining the original text for display and audit.

The skills are complementary, not a mandatory response pipeline. A consuming framework must not treat this directory as an implicit plugin registry or assume that reading every file activates behavior.

## Acceptance checklist

A new entry may join this group only when its behavior is framework-neutral, its owner and consumers are declared in the manifest, its canonical content is explicit, and its success and failure behavior can be tested offline. The entry must not depend on SoulMap-specific doctrine, routing, voice, crisis policy, brand language, web behavior, or private state.

## Expected outcome

A consumer that follows this group can build on a small, inspectable foundation while keeping application policy separate. Soulmate remains useful independently, and SoulMap can consume approved foundation capabilities without absorbing the entire SoulMap skill system.
