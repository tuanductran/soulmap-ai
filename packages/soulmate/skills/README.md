---
name: "soulmate-foundation-skills"
description: "Framework-neutral AI-facing foundation skills for the Soulmate library."
license: "MIT"
---

# Soulmate foundation skills

## Purpose

This directory contains the first five AI-facing foundation skills for Soulmate. They explain reusable contracts and deterministic data capabilities without importing SoulMap's doctrine, routing policy, safety posture, voice, brand, or spiritual frameworks.

These skills are written for a future Soulmate skill artifact. They are not part of the root SoulMap skill bundle, and they do not instruct a consuming framework how to behave as a product.

## Skills in this group

| Skill | Foundation concern | Recommended role |
| --- | --- | --- |
| `contracts.md` | Public input, result, invariant, and failure contracts | Read first when defining or reviewing a shared capability |
| `resource-boundaries.md` | Explicit resource references and loader seams | Use when knowledge or text is resolved from an approved source |
| `knowledge-resolution.md` | Deterministic extraction from selected Markdown sections | Use when structured neutral knowledge is stored as Markdown |
| `text-normalization.md` | Conservative lexical normalization | Use before an explicitly lexical comparison or lookup |
| `data-validation.md` | Bounded JSON parsing and basic field checks | Use at the first boundary for raw JSON input |

## Use this group when

Use these skills when building or reviewing a reusable foundation capability that must work without a particular framework, brand, provider, account, network, database, or LLM. Apply the relevant skill before a consumer-specific policy or presentation layer.

## Do not use this group for

Do not use these skills to select a product framework, activate a route, generate a response persona, enforce a product safety policy, classify a user's meaning, or replace a consumer's domain schema. The foundation explains contracts and mechanics; consumers retain policy, interpretation, and presentation.

## Reading workflow

Read `contracts.md` first to establish the shared contract vocabulary. Then read the skill that matches the boundary being designed. A resource-backed Markdown capability will normally use `resource-boundaries.md` followed by `knowledge-resolution.md`. A raw JSON capability will use `data-validation.md`. A lexical lookup may use `text-normalization.md`, while retaining the original text for display and audit.

The skills are complementary, not a mandatory response pipeline. A consuming framework must not treat this directory as an implicit plugin registry or assume that reading every file activates behavior.

## Acceptance checklist

A new entry may join this group only when its behavior is framework-neutral, its owner and consumers are declared in the manifest, its canonical content is explicit, and its success and failure behavior can be tested offline. The entry must not depend on SoulMap-specific doctrine, routing, voice, crisis policy, brand language, web behavior, or private state.

## Expected outcome

A consumer that follows this group can build on a small, inspectable foundation while keeping application policy separate. Soulmate remains useful independently, and SoulMap can consume approved foundation capabilities without absorbing the entire SoulMap skill system.
