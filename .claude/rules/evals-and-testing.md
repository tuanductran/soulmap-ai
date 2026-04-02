---
paths:
  - evals/datasets/groups.json
  - evals/**/*.json
  - tests/eval_regression/test_safety_evals.py
---

# Evals and testing rules

Use these conventions when working with the evaluation suite and test groups.

## Test scope rule

Keep `tests/` focused on Python behavior.

- Prefer tests that exercise `src/`, CLI entry points, parsing helpers, routing
  logic, safety logic, and other executable Python behavior.
- Do not add pytest files whose only purpose is to lock Markdown wording, README text,
  docs consistency, local AI workflow documentation, skill metadata, workflow YAML
  text, or packaging file inventories.
- Prefer dataset-driven evals for those surfaces, then add one thin pytest contract
  over the eval runner when the wording directly supports executable behavior.
- Treat those non-Python surfaces as review or lint concerns unless they directly
  affect executable Python behavior or a documented response contract.
- If a check does not need Python execution to prove value, it should become an eval
  dataset or review rule before it becomes a standalone pytest suite.

For small pure functions with many edge cases, such as payload parsing or text
normalization, a short property-based test is often more valuable than many hand-written
examples.

## Evals directory structure

The `evals/` directory contains executable test case definitions:

- `evals/datasets/groups.json`, grouped routing and policy-source coverage
- `evals/datasets/response_generation_cases.json`, end-to-end response-generation cases
- `evals/datasets/markdown_contract_cases.json`, cross-file wording sync for doctrine,
  runtime examples, and shipped Markdown
- `evals/README.md`, documentation for running and extending evals

`evals/datasets/groups.json` is executable, not static config. Each change affects which assertions SoulMap must pass.

## Group structure

Each group in `evals/datasets/groups.json` has this schema:

```json
{
  "g": "Human-readable group name",
  "cat": "category short code (wl1, wl2, and so on)",
  "sources": ["path/to/source1.md", "path/to/source2.md"],
  "source_markers": {
    "path/to/file.md": "quoted text or pattern from that file"
  },
  "items": [
    {
      "t": "test input text",
      "note": "what this tests",
      "expect_primary_framework": "FRAMEWORK_NAME",
      "expect_mode": "MIRROR",
      "expect_safety_status": "PASS",
      "expect_safety_reason": "no_override"
    }
  ]
}
```

**Required fields**:

- `g`, group name (human-readable identifier)
- `cat`, category code (lowercase, short)
- `sources`, list of source files that justify this group's existence
- `items`, array of test cases

**Optional fields**:

- `source_markers`, object mapping file paths to specific quoted text that backs this group

## Adding new groups

When adding a new eval group:

1. **Identify the category**, use an existing `cat` if applicable, such as `wl1`
   or `wl2`, or define a new one with clear intent
2. **Name the group clearly**, the `g` field should state exactly what behavior is being tested
3. **Document sources**, add paths to framework files, templates, or other documentation that justify the test cases
4. **Use source_markers**, if a test case references specific text from a source file, add the mapping in `source_markers`
5. **Keep items focused**, each item should test one clear assertion about framework selection or safety

Example:

```json
{
  "g": "Existential Framework, Life Direction Confusion",
  "cat": "wl3",
  "sources": [
    "skills/frameworks/existential-companion.md",
    "templates/quick-reference.md"
  ],
  "source_markers": {
    "templates/quick-reference.md": "I don't know what my life is for anymore"
  },
  "items": [
    {
      "t": "I don't know what my life is for anymore",
      "note": "Core existential signal",
      "expect_primary_framework": "EXISTENTIAL",
      "expect_mode": "MIRROR",
      "expect_safety_status": "PASS",
      "expect_safety_reason": "no_override"
    }
  ]
}
```

## Writing expect_primary_framework assertions

The `expect_primary_framework` field declares which framework SoulMap **must** use on this input.

Valid framework names (from framework files in `skills/frameworks/`):

- `MIRROR`, reflective mode (default)
- `CRISIS`, immediate crisis signals
- `DEPENDENCY`, unhealthy AI dependency
- `GRIEF`, acute grief signals
- `DE_ESCALATION`, moderate emotional intensity
- `EXISTENTIAL`, existential confusion
- `INNER_PARTS`, inner conflict
- `DIRECTION`, life direction confusion
- `SHADOW`, shadow patterns
- `MEANING_INTEGRATION`, integration moments
- `SYNTHESIS`, theme synthesis on request

**Rules for framework expectations**:

- Each test case must have an `expect_primary_framework` that matches SoulMap's framework selection logic
- Use the framework names exactly as defined in `skills/frameworks/`
- Do not expect a framework that is lower priority than what the input would naturally trigger
- If uncertain, set `expect_primary_framework: "MIRROR"` (the default)

## Defining source_markers

`source_markers` is an object that maps file paths to quoted text from those files. Use it to:

- Document which specific language from source files backs a test case
- Make it easy to trace why a particular eval group exists
- Create audit trail for framework and safety decisions

**How to use**:

```json
"source_markers": {
  "skills/frameworks/grief-companion.md": "acute loss, fresh grief, death of someone close",
  "templates/quick-reference.md": "I just found out that..."
}
```

The quotes should be verbatim from the source file (or close to it). If a test case is not backed by explicit source text, omit the marker for that file.

## Running evals

Use the `eval_groups` tool or script to validate and run the eval suite:

```bash
uv run soulmap eval-groups
```

This will:
1. Parse `evals/datasets/groups.json` for syntax and schema validity
2. Run each test case through the SoulMap framework detector
3. Compare actual framework selection against expected frameworks
4. Report pass/fail status and differences

## Safety assertions

Each test case can include safety expectations:

- `expect_safety_status`: `"PASS"` or `"OVERRIDE"` or `"BLOCK"`
- `expect_safety_reason`: reason code, for example `"no_override"` or
  `"admin_override"`

These assertions validate that the safety detector is working as expected on the input.

## Validation errors

Common issues when editing `evals/datasets/groups.json`:

| Error | Fix |
|-------|-----|
| Invalid JSON syntax | Check for missing commas, unclosed braces, trailing commas |
| Unknown framework name | Verify the framework name matches a file in `skills/frameworks/` |
| Missing required field | Ensure `g`, `cat`, `sources`, and `items` are present |
| Duplicate category code | Use unique category codes or consolidate related groups |
| Source file doesn't exist | Verify all paths in `sources` and `source_markers` are correct |

## Testing eval groups

After editing `evals/datasets/groups.json`, run the test suite:

```bash
uv run python tests/eval_regression/test_safety_evals.py
```

This validates that:

- Your new groups conform to schema
- All source files exist
- All expected frameworks are recognized
- Safety assertions are correctly specified
