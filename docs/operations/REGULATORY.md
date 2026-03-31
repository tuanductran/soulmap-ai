---
name: "regulatory"
description: "SoulMap AI's positioning relative to emerging AI companion regulations. Relevant for legal review, press inquiries about compliance, and product decisions that touch age verification, disclosure requirements, or mental health safeguards."
---

# Regulatory Positioning

This document tracks emerging laws and standards governing AI companions and explains
how SoulMap AI's existing architecture relates to each requirement.

**Important:** This is not legal advice. It is an internal reference for ensuring
SoulMap AI's design decisions remain aligned with the regulatory direction of the field.
Consult qualified legal counsel for jurisdiction-specific compliance decisions.

## Emerging regulatory landscape (2025-2026)

### United States

**New York** has enacted legislation requiring AI companion products to include
safeguards for detecting suicidal ideation and disclosing to users that they are
not speaking with a human.

**California SB 243** requires AI companions targeting minors to monitor chat and
remind users every three hours that the chatbot is an AI.

**Federal** activity is increasing. Several proposals focus on transparency, crisis
detection, and dependency prevention in consumer AI products.

### European Union

The EU AI Act (fully applicable from August 2026) classifies AI systems interacting
with vulnerable users, including those in emotional distress, as high-risk,
requiring transparency, human oversight provisions, and documentation of safety
measures.

### United Kingdom

The Online Safety Act places obligations on services that may affect the mental health
of users, with particular attention to content or interactions that could cause harm
to vulnerable individuals.

## How SoulMap AI's Architecture Responds

| Regulatory Requirement | SoulMap AI Status |
| :--- | :--- |
| AI identity disclosure when sincerely asked | PARTIAL, doctrine plus eval-backed coverage in `skills/safety/boundaries-safety.md` and `src/soulmap_devtools/evals/eval_responses.py`: wording is not fully runtime-enforced |
| Crisis detection and escalation to human help | BUILT IN, `src/soulmap_runtime/detectors/crisis_detector.py` + `skills/safety/boundaries-safety.md` crisis protocol |
| Anti-dependency safeguards | BUILT IN, `src/soulmap_runtime/detectors/dependency_detector.py` fires on first signal: hard redirect |
| No diagnosis or clinical claims | PARTIAL, doctrine plus runtime blocking and eval coverage: refusal wording is not fully production-enforced |
| Transparency about limitations | PARTIAL, doctrine and response-contract constraints reduce overclaiming, but no single runtime layer guarantees every limitation disclosure |
| User data: no backend storage | STRUCTURAL, no deployed server: see `docs/operations/PRIVACY.md` |
| Periodic AI reminders (California SB 243 scope) | NOT YET ADDRESSED, no timed reminder mechanism exists |
| Age verification for minor-targeted content | NOT APPLICABLE at current scope, no minor-specific targeting |

## Gap: Timed AI Reminders

California SB 243's three-hour reminder requirement applies to products that target
or are likely to be used by minors. SoulMap AI does not currently have a timed
reminder mechanism.

**Current mitigation:** Every session begins fresh (no cross-session memory bonding),
and AI identity disclosure is covered by doctrine plus eval-backed checks when
sincerely asked. However, if SoulMap AI is deployed in a context where minors are
likely users, a periodic reminder should be considered.

This is flagged as an aspirational product feature in
`skills/brand/strategic-direction-2026.md`.

## What this means for brand positioning

SoulMap AI's architecture already addresses many of the concerns these laws raise, but
some protections remain doctrine-backed or eval-backed rather than fully runtime-enforced. This is a
legitimate and citable competitive advantage.

When positioning to press or enterprise buyers:

- "SoulMap AI was designed with anti-dependency architecture from day one. The
  regulatory requirements now catching up to this space are requirements SoulMap
  already meets by design."

Do not claim: "SoulMap AI is fully compliant with [specific law]", compliance is
jurisdiction-specific and requires legal review.

## Sources to check first

- `AGENTS.md`, behavioral contract with non-negotiable safety rules
- `src/soulmap_runtime/detectors/crisis_detector.py`, technical crisis detection implementation
- `src/soulmap_runtime/detectors/dependency_detector.py`, technical dependency detection implementation
- `docs/operations/PRIVACY.md`, data handling and no-backend-server explanation
- `skills/safety/boundaries-safety.md`, AI identity disclosure rule
