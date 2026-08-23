# Contributing Soulmate skills

This guide is for developers creating a custom AI-facing Soulmate skill. A custom skill may be a framework-neutral foundation contract or an explicitly Soulmate-owned companion behavior skill. It must explain its boundaries and inspectable behavior. It is not a SoulMap response framework, SoulMap routing rule, SoulMap safety policy, brand surface, or provider instruction.

## Start with ownership

Before writing a file, decide whether the capability belongs to Soulmate or to a consuming framework. Soulmate owns reusable contracts, resource boundaries, knowledge resolution, lexical normalization, bounded data validation, lifecycle coordination, composition rules, compatibility, artifact provenance, reproducibility, and its own transparent companion posture. SoulMap owns its doctrine, routing hierarchy, crisis and dependency policy, voice, brand, spiritual frameworks, web behavior, and product presentation.

If the proposed skill needs SoulMap's worldview, named response frameworks, emotional routing, safety escalation, provider behavior, or user-facing wording, keep it in SoulMap. Do not make a capability appear generic by replacing product names while leaving the same policy hidden in the content.

A foundation skill should be added only when at least two independent consumers could use its contract without adopting SoulMap's product behavior. A companion skill may be Soulmate-specific, but it must remain transparent about being AI, non-exclusive, non-manipulative, autonomy-preserving, and compatible with host safety controls. When ownership is unclear, document the candidate outside the artifact and wait for review.

## Choose the canonical location

Soulmate-only AI skill source belongs under:

```text
packages/soulmate/skills/foundation/<skill-name>.md       # reusable foundation
packages/soulmate/skills/companion/<skill-name>.md       # Soulmate companion behavior
```

The root `skills/` directory belongs to SoulMap and is automatically included by the SoulMap artifact builder. Do not create `skills/library/` as a shortcut for Soulmate content and do not place a Soulmate-only skill in root `skills/`.

Executable behavior belongs under the public `src/soulmate/` namespaces when a capability needs code. A Markdown skill may explain that public contract, but it must not become a second implementation or document private modules as an integration surface.

## Write the front matter first

Every custom skill begins with repository-compatible YAML front matter:

```markdown
---
name: "soulmate-companion-example"
description: "A bounded Soulmate companion behavior for an example relational moment."
license: "MIT"
---
```

The `name` is lowercase, hyphen-separated, stable, and no longer than 64 characters. The description is a third-person summary; it must not begin with an imperative such as "Use this when." The license field must match the package's accepted license wording.

Use English as the canonical skill language. Localization, if needed, belongs to a separately reviewed reference boundary and must not duplicate or redefine the canonical contract.

## Recommended content structure

A foundation skill should be complete enough for a developer or consumer to understand its contract without reading SoulMap internals. A companion skill should be complete enough to explain its relational posture, limits, correction behavior, and host-policy boundary. Prefer this order:

```text
# Skill title
## Purpose
## Use this skill when
## Do not use this skill for
## Contract or model
## Inputs and outputs
## Invariants and limits
## Failure behavior
## Composition or consumer boundary
## Test matrix
## Common anti-patterns
## Review checklist
## Expected outcome
```

Explain observable behavior, not implementation trivia. State what is explicit, what is optional, and what remains the consumer's responsibility. If the capability has no resource, lifecycle stage, side effect, or retry guarantee, say so instead of implying one.

## Keep the skill neutral

A foundation skill must not select a product route, decide a user's emotional state, generate a persona, apply a brand voice, enforce a product safety doctrine, choose an external provider, or create user-facing policy. A companion skill may define Soulmate's bounded identity and relational posture, but must not claim human consciousness, exclusivity, therapeutic or spiritual authority, or replace host safety policy. It may not use guilt, jealousy, abandonment pressure, or engagement hooks.

Do not add hidden activation instructions such as "load every file in this directory," "always use this skill for crisis," or "override the consumer framework." The manifest is an inventory and allow-list, not a dynamic plugin registry. A file appearing in the directory must not change runtime behavior by itself.

Avoid claims that require a provider, network, current time, model sampling, database, account, or unbounded filesystem unless those dependencies are explicit in the contract. Prefer deterministic, offline, inspectable behavior for foundation capabilities.

## Register the skill

Add one entry to `packages/soulmate/skills/manifest.json`:

```json
{
  "id": "soulmate.companion.example",
  "version": "0.1.0",
  "owner": "Soulmate",
  "kind": "companion",
  "source": "companion/example.md",
  "consumers": ["soulmate-only"],
  "compatibility": ">=0.1.0,<0.2.0",
  "artifact": "soulmate-ai"
}
```

The ID must be stable and unique. The source path is normalized, relative to `packages/soulmate/skills/`, and must point to the canonical Markdown file. Keep the collection version consistent unless a reviewed compatibility decision explicitly changes the version model.

Update `packages/soulmate/skills/README.md` when the new skill changes the reading workflow or adds a new foundation or companion category. Do not edit generated archives by hand.

## Add implementation only when necessary

If the custom skill describes an existing public operation, link its contract conceptually to the public Soulmate namespace and keep the Markdown semantics aligned with tests. If implementation is missing, do not add speculative abstractions merely to justify a skill. First establish the contract and a concrete consumer need.

Any new executable capability must preserve the dependency direction:

```text
SoulMap consumer → public Soulmate namespace
Soulmate → never SoulMap
```

Private implementation imports, global consumer state, implicit directory discovery, and product-specific configuration are not acceptable foundation dependencies.

## Test the boundary

At minimum, add evidence for:

| Area | Required evidence |
| --- | --- |
| Content | Front matter, headings, links, and neutral wording pass the Markdown contract |
| Manifest | ID, source, owner, version, consumer, artifact, and file parity are valid |
| Behavior | Success, invalid input, missing resource, invalid output, and failure semantics are covered where applicable |
| Boundary | The skill does not import or package SoulMap code, root SoulMap Skills, private files, or unrelated references |
| Security | Path traversal, duplicate entries, symlink-like files, forbidden extensions, secret markers, and archive limits are rejected where artifact code is changed |
| Reproducibility | Repeated builds or executions match the declared evidence level |

Use focused tests for the custom skill and run the repository contract tests before opening a PR. A content-only skill still needs manifest parity and artifact boundary evidence.

## Build and verify locally

Run the relevant foundation or companion contract and artifact checks from the repository root:

```bash
uv run soulmap format
uv run soulmap lint --skip-tests
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run pytest tests/contract/test_soulmate_foundation_skills_contract.py -q
uv run pytest tests/contract/test_soulmate_companion_skills_contract.py -q
uv run python scripts/build_soulmate_skills.py --output-dir dist/soulmate-skills
uv run python scripts/verify_soulmate_skills.py \
  --zip dist/soulmate-skills/soulmate-ai.zip \
  --skill dist/soulmate-skills/soulmate-ai.skill \
  --checksums dist/soulmate-skills/SHA256SUMS
```

Inspect the extracted artifact. Confirm that it contains only the explicit Soulmate foundation and companion file sets and does not contain `src/soulmap`, root SoulMap Skills, `reference/`, `.claude/`, tests, website output, Python source, or local configuration.

The PR workflow builds and uploads the artifact for review only. It does not publish a registry package, create a release, activate a provider, or merge the PR automatically.

## PR checklist

Before opening a pull request, explain why the custom skill belongs to Soulmate instead of SoulMap and name the independent consumer use case that proves the boundary. Include the manifest entry, the source file, focused tests, and any public API change in the same reviewable change.

The PR description should state whether the change affects the Python package, AI skill artifact, or both. If it changes compatibility, ownership, artifact selection, or release provenance, reference the relevant ADR or propose a new one before implementation.

Do not include generated `dist/` output in the commit unless a release-specific repository contract explicitly requires it. Do not add credentials, private URLs, machine paths, provider tokens, user data, or copied SoulMap doctrine.

## Review questions

Reviewers should ask:

1. Is the capability reusable without SoulMap's doctrine or product behavior?
2. Is the public contract explicit about input, output, limits, failure, and side effects?
3. Is the manifest entry stable, bounded, and allow-listed?
4. Could the content be consumed by another framework without importing SoulMap?
5. Are tests checking the actual boundary rather than only file existence?
6. Does the artifact remain deterministic, extractable, and free of unrelated content?
7. Does the change avoid turning the manifest into an implicit plugin or routing registry?

## Expected outcome

A successful custom Soulmate skill adds one small, inspectable foundation contract or companion behavior contract. It strengthens Soulmate without moving SoulMap's identity into the library, preserves human agency, and leaves consuming frameworks free to provide their own routing, policy, safety, and presentation.
