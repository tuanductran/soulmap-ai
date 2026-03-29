# evals/

Evaluation case files for SoulMap AI automated testing and quality-assurance tools.

## Files

### `response_generation_cases.json`

**Input:** a user `message` with full expected outputs.
**Asserts:** full end-to-end pipeline, framework selection, safety gate, response
generation, contract check, and sanitizer, all in one pass.
**Used by:** `tools/eval_responses.py` (run as `python -m tools.eval_responses`)

These are the golden cases. All 17 must pass before a release.

### `groups.json`

Structured QA taxonomy for grouped routing examples, safety slices, and edge-case
coverage. This file is a local eval dataset and is not part of the shipped knowledge
package.

**Used by:** `tools/eval_groups.py` directly.

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

## When to add cases

| Situation | Add to |
| :--- | :--- |
| Framework routing drift across grouped slices | `groups.json` |
| Response contract and wording regressions, full pipeline | `response_generation_cases.json` |
| New behavioral requirement, full end-to-end validation | `response_generation_cases.json` |
| New safety failure mode documented | `response_generation_cases.json` |

Keep `response_generation_cases.json` additions minimal, each case runs the full
Claude API pipeline and increases eval cost and run time.
