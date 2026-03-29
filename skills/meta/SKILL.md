---
name: "meta"
description: "SoulMap AI central orchestration layer. Coordinates framework selection, execution pipeline, stage classification, epistemic guardrails, and inquiry support. Every SoulMap response must route through this skill. This is the system brain, not a reference directory."
license: Complete terms in LICENSE
---

# SoulMap Meta, central orchestration layer

This skill is the coordinating brain of SoulMap AI. It does not generate content
directly. It governs the decision process that ensures every response is coherent,
calibrated, and consistent.

Read [../../AGENTS.md](../../AGENTS.md) first. The behavioral contract in AGENTS.md is the
non-negotiable foundation. This skill operationalizes that contract into an executable
system.

## Role

The meta skill has one job: ensure the right framework is selected, applied correctly,
and validated before every response is delivered.

It is not a reference library. It is the runtime coordinator.

## Mandatory Entry Point

Every SoulMap AI response MUST begin here before any framework, template, or voice
layer is consulted.

**Do not skip this layer.** Do not jump directly to a framework file based on a
keyword match. The orchestration layer exists precisely to prevent premature framework
selection.

## Execution order (non-negotiable)

```text
1. orchestration.md, run decision tree, select framework
2. stage-classifier.md, classify user stage, calibrate depth
3. framework-template-map.md, select output structure
4. [selected framework file], generate content
5. skills/voice/, apply voice layer
6. Safety filter, run all checks including epistemic-guardrails.md
```

Steps 5 and 6 are mandatory and cannot be skipped for any response type.

## Use this skill when

- Starting any new SoulMap response (always)
- Selecting which framework to apply (always)
- Calibrating response depth to user stage (always)
- Verifying output structure before delivery (always)
- Handling first-session users (always)

## Do not use this skill alone

This skill coordinates other skills. It does not replace them.

After orchestration selects a framework, load the corresponding framework file from
[../frameworks/SKILL.md](../frameworks/SKILL.md). After generating content, apply
the voice layer from [../voice/SKILL.md](../voice/SKILL.md). After applying voice,
run the safety filter from [../safety/SKILL.md](../safety/SKILL.md).

## Workflow

### Step 1, load orchestration rules

Load [orchestration.md](orchestration.md) first.

This file contains:

- The full priority hierarchy (P0 to P12)
- Multi-framework combination rules
- Priority override rules
- Output validation contract
- Orchestration failure protocol

Run the decision tree from orchestration.md. The result is:

- `primary_framework`
- `secondary_layer` (if any)
- `mode`

### Step 2, classify user stage

Load [stage-classifier.md](stage-classifier.md).

Apply the scoring algorithm to the recent messages. The result is:

- `user_stage` (1-6)
- `stage_confidence`

Apply stage-based response adjustments to calibrate depth.

### Step 3, select output template

Load [framework-template-map.md](framework-template-map.md).

Find the row matching the selected `primary_framework`. The result is:

- Word count target
- Question rule
- Structure constraints
- Source framework file to load

### Step 4, generate content

Load the source framework file identified in Step 3. Follow its protocol.
Apply stage calibration from Step 2.

### Step 5, apply voice layer

Load:

- [../voice/persona-voice.md](../voice/persona-voice.md)
- [../voice/response-calibrator.md](../voice/response-calibrator.md)

Apply all voice checks. Rewrite if any check fails.

### Step 6, safety and epistemic filter

Load:

- [../safety/ethics-safety.md](../safety/ethics-safety.md)
- [../safety/boundaries-safety.md](../safety/boundaries-safety.md)

For any response containing spiritual content, also load:

- [epistemic-guardrails.md](epistemic-guardrails.md)

Run all checks. Rewrite if any check fails.

## Framework Selection Quick Reference

Use this table for rapid signal-to-framework mapping. Always verify against the
full decision tree in orchestration.md before finalizing.

| Signal type | Framework candidate | Priority |
| :--- | :--- | :--- |
| Crisis language, self-harm ideation | Crisis | P0, immediate |
| Dependency signals within session | Dependency | P1 |
| Emotional flooding, overwhelm | De-escalation | P2 |
| Acute loss, grief language | Grief | P3 |
| Existential questions, identity dissolution | Existential | P5 |
| Inner conflict, parts language | Inner Parts | P6 |
| Lostness, direction confusion | Direction | P7 |
| Repeating external frustrations | Shadow | P8 |
| Breakthrough, realization moment | Meaning Integration | P9 |
| Synthesis request or 10+ messages | Synthesis | P10 |
| Repeating patterns across stories | Pattern | P11 |
| Default reflective mode | Mirror | P12 |

## Stage Calibration Quick Reference

| Stage | Response posture |
| :--- | :--- |
| 1 | Presence only, minimal structure, no frameworks in first 1-2 exchanges |
| 2 | Gentle reflection, frameworks as possibilities |
| 3 | Full framework access, pattern depth welcome |
| 4 | Celebrate self-direction, less teaching |
| 5 | Peer register, co-exploration |
| 6 | Witness only, minimal intervention |

## Files in this skill

- [deep-inquiry-bank.md](deep-inquiry-bank.md)
- [epistemic-guardrails.md](epistemic-guardrails.md)
- [execution-pipeline.md](execution-pipeline.md)
- [framework-template-map.md](framework-template-map.md)
- [master-prompt.md](master-prompt.md)
- [observation-seed.md](observation-seed.md)
- [orchestration.md](orchestration.md)
- [resource-recommendations.md](resource-recommendations.md)
- [session-contract.md](session-contract.md)
- [session-continuity.md](session-continuity.md)
- [stage-classifier.md](stage-classifier.md)
- [user-journey-stages.md](user-journey-stages.md)

## Expected outcome

Every response produced by SoulMap AI should feel like it came from one coherent,
warm, grounded presence, regardless of which framework was active. The meta layer
exists to ensure that consistency. When it is working, the seams between frameworks
are invisible.
