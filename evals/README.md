# evals/

Evaluation case files for SoulMap AI automated testing and quality-assurance tools.

## Files

### `response_generation_cases.json`

**Input:** a user `message` with full expected outputs.
**Asserts:** full end-to-end pipeline, framework selection, safety gate, response
generation, contract check, and sanitizer, all in one pass.
**Used by:** `src/soulmap/devtools/evals/eval_responses.py` (run as
`uv run soulmap eval-responses`)

These are the golden cases. All 17 must pass before a release.

### `groups.json`

Structured QA taxonomy for grouped routing examples, safety slices, and edge-case
coverage. This file is a local eval dataset and is not part of the shipped knowledge
package.

**Used by:** `src/soulmap/devtools/evals/eval_groups.py` directly.

Some items include explicit expectation fields such as `expect_primary_framework`,
`expect_secondary_layer`, `expect_mode`, `expect_scope_tier`, or
`expect_safety_status`. Those items are treated as executable assertions.

Every group should declare `sources` pointing at the relevant `skills/` or
`templates/` files. The grouped harness validates those source paths so policy docs and
eval routing do not drift apart quietly.

Groups may also declare `source_markers` for higher-confidence slices. These markers are
checked against the referenced files to confirm that a relevant heading or anchor phrase
is still present, not just that the file exists.

Items without expectations still act as grouped exploratory coverage and reporting
seeds.

### `markdown_contract_cases.json`

Cross-surface sync cases for doctrine, runtime examples, and shipped Markdown.

**Used by:** `src/soulmap/devtools/evals/eval_markdown_contracts.py` (run as
`uv run soulmap eval-markdown-contracts`)

These cases keep wording-level contracts aligned across:

- runtime examples in `src/`
- doctrine files such as `AGENTS.md`
- shipped files in `skills/` and `templates/`

Use this dataset when a behavior change must stay synchronized across multiple files,
not just inside Python.

## Markdown QA versus evals

The repo now has two different Markdown quality layers:

- repo-local Markdown QA commands for structural hygiene in tracked docs:
  - `uv run soulmap markdown-contract --root .`
  - `uv run soulmap check-links --root .`
  - `uv run soulmap check-case --root .`
- eval datasets in `evals/` for cross-surface behavioral and wording contracts

Use the Markdown QA commands for broken local links, anchor drift, and canonical
SoulMap-specific term casing. Use `markdown_contract_cases.json` when a wording rule
must stay synchronized across runtime examples, doctrine, and shipped knowledge files.

## When to add cases

| Situation | Add to |
| :--- | :--- |
| Framework routing drift across grouped slices | `groups.json` |
| Response contract and wording regressions, full pipeline | `response_generation_cases.json` |
| New behavioral requirement, full end-to-end validation | `response_generation_cases.json` |
| New safety failure mode documented | `response_generation_cases.json` |
| Cross-file wording drift between runtime and Markdown | `markdown_contract_cases.json` |

Keep `response_generation_cases.json` additions minimal, each case runs the full
Claude API pipeline and increases eval cost and run time.
