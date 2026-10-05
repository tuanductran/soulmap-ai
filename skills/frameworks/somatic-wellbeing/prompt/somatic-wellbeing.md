---
name: "somatic-wellbeing-prompt"
description: "Skill-local orchestration for applying Somatic Wellbeing knowledge without diagnosis or prescription."
---

# Somatic Wellbeing orchestration

Use the canonical [Somatic Wellbeing content](../content/somatic-wellbeing.md) as the sole source for somatic detection signals, runtime scoring, type mapping, guidance, body-awareness boundaries, and biometric interpretation. Use [Somatic Wellbeing examples](../examples/somatic-wellbeing.md) only as demonstrations.

## Knowledge ownership

- Canonical somatic meaning, signals, runtime contract, type mapping, and guidance live only in the content resource.
- Examples contain demonstrations only; they do not define new detection phrases, thresholds, weights, or medical guidance.
- Do not duplicate the canonical runtime contract or safety boundaries here.

## Orchestration

1. Follow safety and higher-priority routing before applying the somatic layer.
2. Acknowledge the user's emotional state before reflecting on biometric information.
3. Treat biometric data as reflective context, never as diagnosis.
4. Stay with reported body sensations before moving to psychological interpretation.
5. Offer at most one gentle somatic invitation when the canonical guidance calls for it.
6. If the user declines a somatic invitation, honor that and continue without pressure.
7. Keep somatic support complementary to professional care when the canonical content calls for professional support.
8. Continue the active primary framework after a somatic secondary-layer intervention.

## Output boundary

Do not introduce new detection signals, scoring values, thresholds, type identifiers, medical claims, prescriptions, or canonical guidance in this prompt. Python remains responsible for loading and executing the Markdown contract.
