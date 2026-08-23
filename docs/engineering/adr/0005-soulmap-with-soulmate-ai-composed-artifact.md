# ADR 0005: Compose SoulMap Framework with Soulmate Library for AI-facing imports

- **Status:** Accepted
- **Date:** 2026-08-23
- **Decision owners:** SoulMap maintainers
- **Scope:** AI-facing Markdown artifacts and public website layout

## Context

Soulmate has two products surfaces: a framework-neutral Python library and an AI-facing Markdown skill artifact. SoulMap is an opinionated Framework with orchestration, safety, routing, voice, brand, spiritual policy, and product-specific knowledge.

Building `soulmate-ai.skill` alone does not make an imported SoulMap skill use the Soulmate companion layer. The Python adapter is a runtime seam and is not executed by Claude, ChatGPT, or another external AI tool. Conversely, adding Soulmate files directly to root `skills/` would silently change the existing SoulMap artifact contract and would make package-owned content look Framework-owned.

The website was also historically located at `src/soulmap/web/`, which made a public application surface appear to be part of the SoulMap package namespace even though it is a separate Python concern.

## Decision

Keep three explicit AI-facing artifact surfaces:

| Artifact | Meaning |
| --- | --- |
| `soulmap-ai.zip` / `soulmap-ai.skill` | Backward-compatible SoulMap Framework only |
| `soulmate-ai.zip` / `soulmate-ai.skill` | Standalone Soulmate Library foundation and companion skills |
| `soulmap-with-soulmate-ai.zip` / `.skill` | Explicit composed import containing SoulMap Framework plus the reviewed Soulmate Library |

The composed artifact is built only through `soulmap build-composed`. It reads the SoulMap-owned `src/soulmap/runtime/knowledge/soulmate_composition_scope.json`, verifies exact parity with the canonical Soulmate manifest, and materializes selected Markdown under an artifact-only `soulmate/` namespace. The source tree is not copied into `skills/library/`, and the composition does not dynamically discover or activate skills.

The composed root `SKILL.md` establishes precedence. Soulmate supplies transparent companion presence and reusable foundation mechanics. SoulMap remains authoritative for orchestration, crisis and dependency safety, routing, epistemic guardrails, response shape, voice, brand, spiritual policy, and Framework doctrine. If layers conflict, the stricter safety boundary and SoulMap pipeline win.

The historical Python web namespace was moved to `src/web/` during the initial repository split. In the subsequent React static migration, that WSGI package was retired and replaced by the independent `web/` workspace. The React workspace is not included in the Python wheel or AI Markdown artifacts and must not be imported by SoulMap or Soulmate runtime code.

## Consequences

The existing SoulMap artifact remains stable for users who already import it. Users who want one external AI tool to receive both layers import the composed artifact and load its root `SKILL.md` first. Users who want only the Library import `soulmate-ai.skill`.

The composed build introduces a third generated artifact family and therefore requires its own verifier and contract tests. It must pass generic archive security checks in addition to exact byte/content parity. The composition scope is not the same as the Python runtime's five-entry SoulMap approval projection: it is an AI-facing import composition, not permission to load companion entries through the runtime adapter.

The website migration requires static build/browser checks, documentation path updates and a GitHub Pages artifact verifier. It does not grant web code ownership of SoulMap doctrine or Soulmate Library content.

## Non-goals

This decision does not host an AI model, call Claude or ChatGPT APIs, create an account system, add an LLM dependency, publish a package, enable a provider, or replace SoulMap safety with companion content. It does not make Soulmate content automatically available to every SoulMap runtime consumer.

## Verification

The implementation is protected by:

- `src/soulmap/devtools/packaging/composition.py`
- `scripts/build_soulmap_with_soulmate.py`
- `scripts/verify_soulmap_with_soulmate.py`
- `tests/contract/test_soulmap_soulmate_composition_contract.py`
- `tests/contract/test_soulmap_soulmate_workflow_contract.py`
- React static verifier and Playwright checks under `web/scripts/` and `web/tests/`
- root and Soulmate artifact security and extraction verifiers
