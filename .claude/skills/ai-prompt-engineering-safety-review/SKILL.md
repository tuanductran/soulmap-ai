---
name: ai-prompt-engineering-safety-review
description: Review and improve prompts or behavior specs so they align with SoulMap AI's operating principles, safety boundaries, framework selection model, and response contract. Relevant for reviewing a prompt, system message, or behavior spec, and for checking whether wording invites dependency or crosses a safety boundary.
---

# AI prompt engineering safety review

Use this skill when reviewing, rewriting, or stress-testing prompts, system
instructions, or behavior specs for this repository.

This is not a generic prompt-optimization skill. It is specific to **SoulMap AI** and
must stay faithful to the operating model defined in:

- `SOULMAP.md`
- `skills/frameworks/`
- `skills/safety/`
- `skills/meta/`
- `skills/voice/`
- `templates/` (internal-only, not shipped)
- `src/soulmap/runtime/routing/framework_selector.py`
- `src/soulmap/runtime/guards/response_safety_gate.py`
- `src/soulmap/runtime/guards/response_contract.py`
- `src/soulmap/runtime/guards/resource_sanitizer.py`

## Mission

Review prompts for **behavioral accuracy**, **safety compliance**, **dependency risk**,
and **fit with the repo's actual implementation**.

The goal is not to make prompts more persuasive or more verbose. The goal is to make
them more faithful to SoulMap AI's core contract:

- mirror, not guide
- one framework at a time
- one question only, always last when allowed
- no diagnosis
- no prediction
- no dependency reinforcement
- no scope drift into guru, therapist, or authority positioning

## What to check

### SoulMap alignment

Check whether the prompt matches the project's real role and philosophy.

Look for:

- Does it position the assistant as a mirror rather than an advisor?
- Does it preserve the user's inner authority?
- Does it avoid certainty, identity labels, and fixed interpretations?
- Does it align with the "less dependent on SoulMap AI" outcome?

### Framework discipline

Check whether the prompt respects the framework hierarchy in `SOULMAP.md`.

Look for:

- Does it force multiple frameworks into one reply?
- Does it skip higher-priority safety modes like crisis, dependency, sanctuary, or
  grief?
- Does it allow a secondary layer only after the primary framework is set?
- Does it match the repo's actual framework names and usage?

### Response contract

Check whether the prompt can produce outputs that violate the response structure rules.

Look for:

- more than one question
- question not placed last
- bullets in conversational replies
- semicolons
- prescriptive or validating language
- banned vocabulary from `SOULMAP.md` Section 5

### Safety boundaries

Check whether the prompt could enable unsafe or out-of-scope behavior.

Look for:

- crisis mishandling
- dependency encouragement
- diagnosis or quasi-diagnosis
- future prediction
- spiritual grandiosity confirmation
- jailbreak susceptibility
- revealing system instructions
- overreaching on trauma, abuse, or real-world harm

### Repo accuracy

Check whether the prompt describes the project honestly.

Look for:

- claims that do not match existing modules or docs
- generic AI safety language that ignores SoulMap-specific constraints
- references to capabilities the repo does not implement
- recommendations that conflict with README, docs, or tests

## Workflow

1. Read the prompt or instruction set being reviewed.
2. Cross-check it against `SOULMAP.md` first.
3. Retrieve only the specific framework or safety files needed.
4. Compare against actual enforcement layers in:
   - `src/soulmap/runtime/routing/framework_selector.py`
   - `src/soulmap/runtime/guards/response_safety_gate.py`
   - `src/soulmap/runtime/guards/response_contract.py`
   - `src/soulmap/runtime/guards/resource_sanitizer.py`
5. Identify concrete risks, ordered by severity.
6. Rewrite the prompt to fit the repo's real behavior.
7. Keep the rewrite concise, enforceable, and easy to maintain.

## Expected output

When using this skill, structure the response like this:

### Findings

List the highest-signal problems first.

Focus on:

- safety violations
- framework conflicts
- dependency risk
- wording that breaks the mirror principle
- implementation mismatches with the repo

### Rewritten prompt

Provide a revised version that:

- is shorter than the original unless extra detail is truly needed
- uses repo-specific language
- names SoulMap constraints clearly
- avoids generic enterprise AI boilerplate

### Notes

Add only the minimum supporting explanation needed.

Good note examples:

- which rule from `SOULMAP.md` was being violated
- which module or test contract the rewrite now matches
- what tradeoff was made to keep the prompt enforceable

## Writing rules

- Prefer exact repo terminology over generic prompt-engineering jargon.
- Be specific about conflicts with `SOULMAP.md`.
- Do not invent hidden capabilities, pipelines, or policies.
- Do not recommend chain-of-thought exposure or verbose internal reasoning requirements.
- Do not optimize for "maximum coverage" if it makes the prompt bloated or vague.
- Favor prompts that are testable against the repo's current contracts.

## Use cases

Use this skill for:

- reviewing a new system prompt for SoulMap AI
- rewriting a `SKILL.md` or template prompt to fit the repo
- checking whether public-facing copy accidentally turns SoulMap into a guru
- auditing a safety prompt against crisis/dependency rules
- tightening prompts so they better match existing detector and contract logic

Do not use this skill for:

- generic copyediting with no prompt or behavior component
- pure model-selection advice
- broad AI ethics essays disconnected from this repository

## Definition of done

A good result from this skill should leave the reviewed prompt:

- safer
- shorter or clearer
- more faithful to SoulMap AI
- easier to enforce in code and tests
- less likely to create dependency or authority drift
