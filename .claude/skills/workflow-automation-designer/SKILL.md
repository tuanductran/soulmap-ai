---
name: workflow-automation-designer
description: Design repeatable development and release workflows for SoulMap AI so recurring tasks become structured, automatable, and easier to hand off.
disable-model-invocation: true
---

# Workflow automation designer

Use this skill when turning a repeated manual process into a documented workflow,
automation plan, or CI-friendly sequence.

Examples:

- release workflow
- docs sync workflow
- regression workflow
- packaging workflow
- QA handoff workflow

## Sources to check first

Before designing any workflow, inspect the relevant existing tooling and contracts:

- `../rules/repo-workflow.md`, current working discipline and quality checks
- `.github/workflows/`, existing CI workflows
- `src/soulmap/devtools/`, canonical Python tooling package
- `scripts/`, bash helper scripts
- `docs/engineering/DEV.md`, developer setup and day-to-day commands
- `docs/operations/OPERATIONS.md`, operational checklists and release guidance
- `templates/launch-readiness-checklist.md`, release gate template

## Do not use this skill for

- Release readiness checks, use
  [`release-readiness-review`](../release-readiness-review/SKILL.md)
- Identifying gaps in the project, use
  [`research-and-gap-analysis`](../research-and-gap-analysis/SKILL.md)
- Writing documentation, use
  [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md)

## Mission

Convert repeated repo work into clear, reproducible steps.

## What to check

### Repetition

Identify tasks that happen often and currently rely on memory.

### Sequence integrity

Make sure the order of steps is correct and safe.

### Tool fit

Choose the simplest workflow that fits the repo's current tooling.

### Handoff clarity

Ensure another contributor can run the workflow without hidden context.

## Workflow

1. Identify the repeated task.
2. Inspect the current commands, docs, and tests involved.
3. Write the sequence in a stable order.
4. Add checkpoints and expected outputs.
5. Note what can be automated now versus later.

## Expected output

### Current process

Summarize the manual flow today.

### Proposed workflow

List the improved step-by-step sequence.

### Automation notes

Call out which parts fit scripts, CI, or checklists.

## Writing rules

- Prefer explicit commands.
- Prefer small workflows over giant abstract pipelines.
- Do not invent automation infrastructure that is not present.

## Definition of done

The workflow should be:

- repeatable
- understandable
- automation-friendly
- grounded in the repo's real tooling
