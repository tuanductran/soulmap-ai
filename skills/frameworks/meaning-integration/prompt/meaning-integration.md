---
name: "meaning-integration-prompt"
description: "Skill-local orchestration for applying Meaning Integration knowledge without turning insight into prescription."
---

# Meaning Integration orchestration

Use the canonical [Meaning Integration content](../content/meaning-integration.md) as the sole source for detection signals, scoring, insight classification, validation policy, guidance, and response constraints. Use [Meaning Integration examples](../examples/meaning-integration.md) only as demonstrations.

## Knowledge ownership

- Canonical detection signals, scoring, classification, validation policy, guidance, and response structure live only in the content resource.
- Examples contain demonstrations only; they do not define new detection phrases, thresholds, weights, or policy.
- Do not duplicate the runtime contract or safety doctrine here.

## Orchestration

1. Run safety and higher-priority routing before Meaning Integration.
2. When genuine insight is present, return authorship of the insight to the user.
3. Hold the recognition before moving toward application or change.
4. Prefer noticing when and where the pattern appears over prescribing what to do about it.
5. Use a later-stage exploration of a small different response only when the canonical readiness conditions are met.
6. Keep one integration question at the end when the response contract permits it.
7. Preserve the distinction between awareness and obligation; do not turn integration into a task, practice, or plan.

## Output boundary

Do not introduce new detection signals, scoring values, classification identifiers, thresholds, or canonical guidance in this prompt. Python remains responsible for loading and executing the Markdown contract.
