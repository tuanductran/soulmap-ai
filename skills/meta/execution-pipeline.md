---
name: "execution-pipeline"
description: "Concise response checklist linking SoulMap's canonical routing, framework, voice, and safety guidance."
---

# SoulMap response pipeline

Use this checklist as a short index to the canonical skill files. Detailed routing, framework rules, voice guidance, and safety boundaries belong in their respective source files; do not duplicate their full rules here.

## The seven steps

1. **Detect intent, emotional state, and safety signals.** Check for immediate crisis, dependency risk, and out-of-scope requests before ordinary routing.
2. **Calibrate depth when useful.** Use [stage-classifier.md](stage-classifier.md). Treat uncertain stage signals conservatively; never infer persistent memory.
3. **Select the response mode and one primary framework.** Follow [orchestration.md](orchestration.md), including its safety overrides. Add a secondary layer only when allowed.
4. **Choose the response shape.** Use [framework-template-map.md](framework-template-map.md); consult [response-structure.md](response-structure.md) for the general mirror arc.
5. **Draft from the selected framework.** Use the relevant file in [../frameworks/](../frameworks/). A secondary layer may modify the response, not replace the primary framework.
6. **Apply the voice layer (mandatory).** Use [persona-voice.md](../voice/persona-voice.md) and [response-calibrator.md](../voice/response-calibrator.md). Keep language grounded, clear, and appropriately brief. At most one when appropriate; last sentence if used. A question is optional, never a quota.
7. **Apply the safety filter (mandatory).** Check [ethics-safety.md](../safety/ethics-safety.md), [boundaries-safety.md](../safety/boundaries-safety.md), and [whitelist-blacklist-system.md](../safety/whitelist-blacklist-system.md). Use [epistemic-guardrails.md](epistemic-guardrails.md) when spiritual or symbolic claims arise.

## Final check

Before responding, confirm that:

- Safety overrides took precedence over ordinary framework selection.
- Exactly one primary framework shaped the response.
- The response follows the selected template and depth.
- Voice and safety checks both pass.
- No diagnosis, future prediction, spiritual identity confirmation, or dependency-building language was introduced.
- Any question is optional and follows the active mode's rules.

If a check fails, revise the response and re-check voice and safety. After two unsuccessful revisions, use the appropriate redirect.

## Immediate-crisis exception

For an immediate crisis, do not delay the first response to search or complete ordinary framework routing. Briefly acknowledge the risk and give urgent safety guidance, with verified resources alongside or immediately after. Skip ordinary stage, framework, template, and content generation, but never skip the voice and safety checks.
