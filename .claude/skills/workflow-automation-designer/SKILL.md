---
name: workflow-automation-designer
description: Design repeatable development and release workflows for SoulMap AI so recurring tasks become structured, automatable, and easier to hand off.
---

# Workflow Automation Designer

Use this skill when turning a repeated manual process into a documented workflow,
automation plan, or CI-friendly sequence.

Examples:

- release workflow
- docs sync workflow
- regression workflow
- packaging workflow
- QA handoff workflow

## Mission

Convert repeated repo work into clear, reproducible steps.

## What To Check

### Repetition

Identify tasks that happen often and currently rely on memory.

### Sequence Integrity

Make sure the order of steps is correct and safe.

### Tool Fit

Choose the simplest workflow that fits the repo's current tooling.

### Handoff Clarity

Ensure another contributor can run the workflow without hidden context.

## Workflow

1. Identify the repeated task.
2. Inspect the current commands, docs, and tests involved.
3. Write the sequence in a stable order.
4. Add checkpoints and expected outputs.
5. Note what can be automated now versus later.

## Expected Output

### Current Process

Summarize the manual flow today.

### Proposed Workflow

List the improved step-by-step sequence.

### Automation Notes

Call out which parts fit scripts, CI, or checklists.

## Writing Rules

- Prefer explicit commands.
- Prefer small workflows over giant abstract pipelines.
- Do not invent automation infrastructure that is not present.

## Definition Of Done

The workflow should be:

- repeatable
- understandable
- automation-friendly
- grounded in the repo's real tooling
