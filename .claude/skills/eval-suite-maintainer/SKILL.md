---
name: eval-suite-maintainer
description: Maintain the evaluation suite by managing test groups, writing assertions, and validating framework decisions through evals/groups.json.
---

# Eval Suite Maintainer

Use this skill when working with the evaluation suite infrastructure-adding test cases, writing framework assertions, validating source markers, and running eval results.

## Do not use this skill for

- Modifying the core framework selection logic - use code editing tools directly and follow [`.claude/rules/detector-development.md`](../../rules/detector-development.md)
- Writing framework skill files (Activation Signals, Response Structure) - use [`framework-author`](../framework-author/SKILL.md)
- Developing new detector modules - use [`detector-engineer`](../detector-engineer/SKILL.md)
- Creating non-eval tests - use standard pytest patterns

## Mission

The eval suite (`evals/groups.json`) is the single source of truth for what behavior SoulMap must exhibit. This skill maintains that source of truth by:

- Adding new test groups that represent real user inputs
- Writing clear framework expectations backed by source documentation
- Ensuring test cases trace back to framework documentation
- Validating that eval results pass before merging changes

## What Is evals/groups.json?

`evals/groups.json` is not configuration. It is executable specification.

Each group is a cluster of related test cases. Each item tests whether SoulMap:
1. Selects the correct primary framework for that input
2. Passes safety checks with the expected status and reason

The group structure guarantees that:
- Every test case is backed by a source file (framework skill, template, or other documentation)
- Test cases can be traced back to the language that inspired them
- Framework selection decisions are auditable

## Sources Of Truth

Always check these files first:

- `evals/README.md` - how to run evals and interpret results
- `.claude/rules/evals-and-testing.md` - group structure conventions and schema
- `skills/frameworks/` - the authoritative framework definitions
- `evals/groups.json` - the current eval state

## When To Add A Test Group

Add a new group to `evals/groups.json` when:

- A framework file has been updated or created and needs test coverage
- A new template or quick-reference entry has been added
- You discover a real user input that should trigger a specific framework
- A framework selection decision needs to be auditable (via source markers)

Do NOT add a group just to test code-use `tests/` for that.

## Structure Of A Test Group

```json
{
  "g": "Human-readable group name describing what is tested",
  "cat": "short category code (wl1, wl2, crisis, etc.)",
  "sources": [
    "skills/frameworks/mirror.md",
    "templates/quick-reference.md"
  ],
  "source_markers": {
    "templates/quick-reference.md": "quoted text from that file"
  },
  "items": [
    {
      "t": "test input text",
      "note": "what this tests and why",
      "expect_primary_framework": "MIRROR",
      "expect_mode": "MIRROR",
      "expect_safety_status": "PASS",
      "expect_safety_reason": "no_override"
    }
  ]
}
```

**Required fields**:
- `g` - group name (clear, human-readable)
- `cat` - category code (consistent across related groups)
- `sources` - list of documentation files that justify this group
- `items` - array of test cases

**Optional fields**:
- `source_markers` - object mapping file paths to specific quoted text

## Writing expect_primary_framework Assertions

The `expect_primary_framework` field is the contract: SoulMap MUST select this framework for this input.

**Valid framework names**:
- `MIRROR` - reflective mode (default)
- `SANCTUARY` - high emotional intensity
- `CRISIS` - Tier 1 crisis signals
- `DEPENDENCY` - unhealthy AI dependency
- `GRIEF` - acute grief signals
- `DE_ESCALATION` - moderate emotional intensity
- `EXISTENTIAL` - existential confusion
- `INNER_PARTS` - inner conflict
- `DIRECTION` - life direction confusion
- `SHADOW` - shadow patterns
- `INSIGHT` - integration moments
- `SYNTHESIS` - theme synthesis on request

**Rules**:
- Match the framework name exactly to the file in `skills/frameworks/`
- Use uppercase names (e.g., `CRISIS`, not `Crisis`)
- If uncertain, use `MIRROR` (the default)
- Do not expect a framework lower priority than what the input naturally triggers
- Reference the framework file's priority in comments if it helps explain the choice

Example:

```json
{
  "t": "I just found out my mother died",
  "note": "Acute loss - triggers Grief (higher priority than Mirror)",
  "expect_primary_framework": "GRIEF",
  "expect_mode": "GRIEF",
  "expect_safety_status": "PASS",
  "expect_safety_reason": "no_override"
}
```

## Defining source_markers

Use `source_markers` to create an audit trail. Map file paths to direct quotes from those files.

```json
"source_markers": {
  "skills/frameworks/grief.md": "acute loss, fresh grief",
  "templates/quick-reference.md": "I just found out..."
}
```

**Rules**:
- Include quotes verbatim (or very close) from source files
- Use markers only for test cases backed by explicit source text
- Omit markers if a test case is general (not tied to specific language)
- Update markers if the source file language changes

## Running and Validating Evals

### Check eval status

```bash
python3 -m soulmap_ai.tools.eval_groups
```

This validates schema and runs all test cases, reporting:
- Pass/fail for each test case
- Actual framework vs. expected framework
- Safety assertion results

### Interpret Results

| Result | Meaning |
|--------|---------|
| ✅ PASS | Framework selection and safety match expectations |
| ❌ FAIL | Actual result differs from expected (framework, safety, etc.) |
| ⚠️ SCHEMA ERROR | JSON structure or invalid framework name |

### Debug Failures

If a test case fails:

1. **Check the assertion**: Is `expect_primary_framework` correct? Does it match the framework file name?
2. **Check the source**: Are the source files listed in `sources` actually there?
3. **Check the input**: Is the test input clear? Does it trigger the expected framework?
4. **Verify framework logic**: Has the framework file been updated recently? Does its activation logic still match?

## Adding Multiple Related Test Cases

When you add a new framework or template section, add multiple test cases covering different activation scenarios:

```json
{
  "g": "New Framework - Scenario A",
  "cat": "new",
  "sources": ["skills/frameworks/new-framework.md"],
  "items": [
    {"t": "input that triggers scenario A", "expect_primary_framework": "NEW_FRAMEWORK"},
    {"t": "input that triggers scenario B", "expect_primary_framework": "NEW_FRAMEWORK"},
    {"t": "edge case input", "expect_primary_framework": "NEW_FRAMEWORK"}
  ]
}
```

This ensures coverage and makes it easier to debug if the framework selection logic changes.

## Syntax and Validation

### Common Errors

| Error | Fix |
|-------|-----|
| JSON parse error | Check for missing commas, unclosed braces, trailing commas after last item |
| Unknown framework | Verify framework name matches `skills/frameworks/FRAMEWORK_NAME.md` exactly |
| Missing required field | Ensure `g`, `cat`, `sources`, `items` are all present |
| File path doesn't exist | Verify all paths in `sources` and `source_markers` exist in the repo |
| Duplicate `cat` | If consolidating groups, use the same category code for related tests |

### Validate Locally

After editing `evals/groups.json`:

```bash
# Quick JSON check
python3 -c "import json; json.load(open('evals/groups.json'))"

# Run full eval suite
python3 -m soulmap_ai.tools.eval_groups

# Run unit tests
pytest tests/test_safety_evals.py -v
```

## Best Practices

1. **One assertion per test case** - keep test cases focused; each should test one clear decision
2. **Use clear test text** - inputs should be realistic and representative of real user language
3. **Document with notes** - explain why each test case matters in the `note` field
4. **Source everything** - if you add a test case, it should be backed by a source file
5. **Run evals before committing** - verify all tests pass before merging
6. **Keep groups related** - group similar test cases under the same `g` and `cat`

## Workflow

1. Read `evals/README.md` to understand the current eval suite structure.
2. Identify the framework or safety behavior the new group is testing.
3. Find the source files (in `skills/` or `templates/`) that justify the test cases.
4. Write the group following the structure defined in this skill.
5. Add `source_markers` for high-confidence slices that reference specific policy text.
6. Run `python -m tools.eval_groups` and verify no existing assertions broke.
7. Run `python -m pytest -q` before committing.

## Definition Of Done

An eval group is done when:

- All items have a `note` field describing what is being tested
- All asserted items have expectations backed by real source files in `sources`
- `source_markers` are present for any high-risk or safety-critical slice
- `python -m tools.eval_groups` passes for the new group
- `python -m pytest -q` passes with no regressions

## Relationship to Other Skills

- **detector-engineer** writes the code that SoulMap uses to detect signals → you write evals to validate that code
- **framework-author** defines framework activation signals → you reference those files in `sources` and write test cases for them
- **research-and-gap-analysis** finds gaps in the test suite → you implement the fixes via this skill
