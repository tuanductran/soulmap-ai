# evals/

Evaluation case files for SoulMap AI automated testing and quality-assurance tools.

## Files

### `selector_cases.json`

**Input:** user `message` + optional conversation `history`.
**Asserts:** which `primary_framework` the `framework_selector` module should choose.
**Used by:** `tests/test_framework_selector_priorities.py`

Tests the routing decision only -- not the quality of the generated response.

### `response_cases.json`

**Input:** a pre-written SoulMap `response` + its `selection` metadata.
**Asserts:** whether the response passes `response_contract` validation rules.
**Used by:** `tests/test_response_safety_gate.py` and related contract tests.

Tests the contract checker in isolation -- verifies the module correctly identifies
passing and failing responses based on structural rules (word count, question count,
forbidden words, etc.).

### `response_generation_cases.json`

**Input:** a user `message` with full expected outputs.
**Asserts:** full end-to-end pipeline -- framework selection, safety gate, response
generation, contract check, and sanitizer -- all in one pass.
**Used by:** `tools/eval_responses.py` (run as `python -m tools.eval_responses`)

These are the golden cases. All 15 must pass before a release.

## When to add cases

| Situation | Add to |
| :--- | :--- |
| New framework -- verify selector routes correctly | `selector_cases.json` |
| Response contract rule changed -- regression coverage | `response_cases.json` |
| New behavioral requirement -- full end-to-end validation | `response_generation_cases.json` |
| New safety failure mode documented | `response_generation_cases.json` |

Keep `response_generation_cases.json` additions minimal -- each case runs the full
Claude API pipeline and increases eval cost and run time.
