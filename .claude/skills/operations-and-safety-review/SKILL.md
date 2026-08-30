---
name: operations-and-safety-review
description: Review operational safety, privacy, consent, and incident-handling guidance so SoulMap AI deployment practices stay aligned with the repo's safety posture.
disable-model-invocation: true
---

# Operations and safety review

Use this skill when reviewing deployment-facing guidance, safety operations, privacy
boundaries, or consent-sensitive features.

Relevant files include:

- `docs/operations/OPERATIONS.md`
- `SOULMAP.md`
- `skills/safety/`
- `src/soulmap/runtime/guards/response_safety_gate.py`
- `src/soulmap/runtime/experimental/biometric_ingest.py`
- `src/soulmap/runtime/memory/memory_ledger.py`

## Do not use this skill for

- Reviewing conversational prompt behavior or response safety rules, use
  [`ai-prompt-engineering-safety-review`](../ai-prompt-engineering-safety-review/SKILL.md)
- Writing or updating technical docs, use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md)
- Editing knowledge files under `skills/` (shipped) or `templates/` (internal-only), use
  [`knowledge-base-maintainer`](../knowledge-base-maintainer/SKILL.md)

## Mission

Ensure operational guidance matches the ethical and safety posture of SoulMap AI.

## What to check

### Safety escalation

Check whether crisis, dependency, and harm scenarios are handled clearly and early.

### Privacy and consent

Check whether docs are explicit about:

- minimal retention
- sensitive content handling
- explicit user consent
- opt-in versus default behavior

### Incident readiness

Check whether operational docs say what to do when the system behaves unsafely.

### Deployment honesty

Ensure deployment guidance does not imply stronger safeguards than the repo actually
implements.

## Workflow

1. Read the operations or safety doc.
2. Compare it against the actual modules and `SOULMAP.md`.
3. Identify operational gaps or overclaims.
4. Tighten the guidance with concrete, minimal corrections.

## Expected output

### Findings

List the highest-risk operational or safety gaps first.

### Updated guidance

Provide the revised wording or checklist.

### Residual risks

Mention any areas that still depend on product-layer implementation outside the repo.

## Writing rules

- Prefer explicit consent language.
- Prefer fail-closed reasoning over optimistic assumptions.
- Keep safety guidance actionable and concrete.

## Definition of done

Operational guidance should be:

- safer
- more honest
- more actionable
- more consistent with the actual implementation
