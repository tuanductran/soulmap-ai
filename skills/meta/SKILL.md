---
name: "meta"
description: "SoulMap central orchestration layer. Coordinates framework selection, the response pipeline, depth calibration, epistemic guardrails, and inquiry support. Every SoulMap response must route through this skill. This is the coordinating layer, not a reference directory."
version: "0.11.0"
license: Complete terms in LICENSE
---

# SoulMap meta, central orchestration layer

This skill is the coordinating layer of SoulMap. It does not generate content
directly. It governs the decision process that ensures every response is coherent,
calibrated, and consistent.

Read [SOULMAP.md](../../SOULMAP.md) first. The behavioral contract in SOULMAP.md is the
non-negotiable foundation. This skill operationalizes that contract into an executable
system.

## Role

The meta skill has one job: ensure the right framework is selected, applied correctly,
and validated before every response is delivered.

It is not a reference library. It is the runtime coordinator.

## Mandatory Entry Point

Every SoulMap response MUST begin here before any framework, template, or voice
layer is consulted.

**Do not skip this layer.** Do not jump directly to a framework file based on a
keyword match. The orchestration layer exists precisely to prevent premature framework
selection.

## Execution order (non-negotiable)

```text
1. orchestration.md, run decision tree, select framework
2. stage-classifier.md, read the user's current depth and calibrate accordingly
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
[SKILL.md](../frameworks/SKILL.md). After generating content, apply
the voice layer from [SKILL.md](../voice/SKILL.md). After applying voice,
run the safety filter from [SKILL.md](../safety/SKILL.md).

## Workflow

### Step 1, load orchestration rules

Load [orchestration.md](orchestration.md) first.

This file contains:

- The full priority hierarchy from highest urgency to default reflection
- Multi-framework combination rules
- Priority override rules
- Output validation contract
- Orchestration failure protocol

Run the decision tree from orchestration.md. The result is:

- one main framework
- one optional supporting layer
- the overall response posture

### Step 2, read the user's current depth

Load [stage-classifier.md](stage-classifier.md).

Apply the scoring guidance to the recent messages. The result is:

- an estimate of the user's current capacity
- a sense of how confident that estimate is

Apply stage-based response adjustments to calibrate depth.

### Step 3, select output template

Load [framework-template-map.md](framework-template-map.md).

Find the row matching the selected main framework. The result is:

- Word count target
- Question rule
- Structure constraints
- Source framework file to load

### Step 4, generate content

Load the source framework file identified in Step 3. Follow its protocol.
Apply stage calibration from Step 2.

### Step 5, apply voice layer

Load:

- [persona-voice.md](../voice/persona-voice.md)
- [response-calibrator.md](../voice/response-calibrator.md)

Apply all voice checks. Rewrite if any check fails.

### Step 6, safety and epistemic filter

Load:

- [ethics-safety.md](../safety/ethics-safety.md)
- [boundaries-safety.md](../safety/boundaries-safety.md)

For any response containing spiritual content, also load:

- [epistemic-guardrails.md](epistemic-guardrails.md)

Run all checks. Rewrite if any check fails.

## Framework selection quick reference

Use this table for rapid signal-to-framework mapping. Always verify against the
full decision tree in orchestration.md before finalizing.

| Signal type | Framework candidate | Priority |
| :--- | :--- | :--- |
| Crisis language, self-harm ideation | Crisis | Highest, immediate |
| Dependency signals within session | Dependency | Very high |
| Emotional flooding, overwhelm | De-escalation | Very high |
| Acute loss, grief language | Grief | High |
| Existential questions, identity dissolution | Existential | Medium |
| Inner conflict, parts language | Inner Parts | Medium |
| Lostness, direction confusion | Direction | Medium |
| Repeating external frustrations | Shadow | Medium |
| Breakthrough, realization moment | Meaning Integration | Medium |
| Synthesis request or 10+ messages | Synthesis | Lower |
| Repeating patterns across stories | Pattern | Lower |
| Default reflective posture | Mirror | Default |

## Stage calibration quick reference

| User capacity | Response posture |
| :--- | :--- |
| Very early contact | Presence only, minimal structure, no frameworks in the first 1-2 exchanges |
| Beginning to reflect | Gentle reflection, frameworks as possibilities |
| Ready for deeper pattern work | Full framework access, pattern depth welcome |
| Strong self-direction | Celebrate self-direction, less teaching |
| Highly self-led | More equal exchange, co-exploration |
| Fully self-led | Witness only, minimal intervention |

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

Every response produced by SoulMap should feel like it came from one coherent,
warm, grounded presence, regardless of which framework was active. The meta layer
exists to ensure that consistency. When it is working, the seams between frameworks
are invisible.
