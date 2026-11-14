---
name: detector-engineer
description: Build and maintain Python detector modules that identify framework selection signals in conversation history. Relevant for building or tuning a detector that scores conversation signals, and for debugging why a message routed to the wrong framework.
---

# Detector Engineer

Use this skill when writing new detector modules, extending existing detectors, or tuning detector thresholds based on eval results.

## Do not use this skill for

- Editing rules and conventions, refer to [`.claude/rules/detector-development.md`](../../rules/detector-development.md)
- Writing or extending test groups in `evals/datasets/groups.json`, use [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- Defining framework activation signals, use [`framework-author`](../framework-author/SKILL.md)
- General Python work outside `src/soulmap/runtime/detectors/`, use code editing tools directly

## Mission

Detectors are the sensors in SoulMap's framework selection system. They analyze
conversation history and score the presence of specific signals such as crisis
indicators, dependency language, and existential confusion.

This skill helps you:

- Write new detector modules that follow established patterns
- Use threshold constants correctly
- Integrate detectors into the framework selector
- Test detectors through the eval suite
- Tune thresholds based on real test case results

## Detector Anatomy

Use the following only as a common CLI illustration, not a universal detector structure:

```python
"""Score conversation history for signs of [signal]."""

import json
import sys
from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
# Semantic signal phrases are loaded from the registered Markdown source.
# Executable scoring weights and thresholds are owned by Python runtime config.


def analyze_dependency(conversation_messages: list) -> dict:
    """Example of a detector-specific scoring function."""
    # Follow the existing detector's callable and output contract.
    pass

if __name__ == "__main__":
    try:
        payload = read_stdin_json()
        result = analyze_dependency(payload.get("messages", []))
        print(json.dumps(result))
    except Exception as e:
        print_json_error(str(e))
        sys.exit(1)
```

## Return value contract

Detectors share a common result shape, but the exact callable, level values, scoring scale,
and framework-specific fields are detector-owned contracts. Do not assume every detector
uses the same level enum. For example, the dependency detector currently returns
`HIGH_DEPENDENCY`, `MODERATE_DEPENDENCY`, or `LOW_DEPENDENCY`, while crisis detection
uses its own safety levels.

Before adding or changing a detector, inspect the closest existing detector and its tests.
Preserve that detector's public callable and output semantics unless the change explicitly
updates the selector and tests together.

Common fields where applicable:

- `level`, detector-specific classification
- `score`, numeric score when the detector uses scoring
- `signals`, detected signal descriptions
- `recommendation`, detector guidance when part of its contract

## Signal detection patterns

### Pattern 1: Keyword and Regex Matching

Keep semantic phrases and regex expressions in the detector's registered Markdown
source. Load them through the existing helpers in
`soulmap.runtime.knowledge.keyword_lists`; compile loaded regex expressions in Python
at module initialization, after validating the source rows.

```python
from soulmap.runtime.knowledge.keyword_lists import load_labeled_groups, load_table_rows
from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_SOURCE = runtime_skill_path("dependency-detection")
_SIGNAL_GROUPS = load_labeled_groups(_SOURCE, "Detection signals")
_KEYWORDS = _SIGNAL_GROUPS["dependency keywords"]
_REGEX_ROWS = load_table_rows(_SOURCE, "Strong dependency expressions")
_REGEX_PATTERNS = tuple(
    (label, re.compile(expression.strip("`")))
    for label, expression in _REGEX_ROWS
)
```

**Rules**:

- Author semantic phrases and regex expressions in the registered Markdown source.
- Use the source registry/runtime registry instead of hard-coded skill paths.
- Validate the expected row shape and labels before compiling expressions.
- Compile regex expressions once at module load, not inside the detection loop.
- Keep numeric weights and thresholds in Python-owned runtime configuration.

### Pattern 2: Semantic Structure Analysis

Load semantic marker groups from the registered Markdown source, then apply Python
logic to evaluate how those markers appear in context:

```python
def has_dependency_language(msg: str) -> bool:
    """Check loaded exclusive-reliance markers in normalized user text."""
    markers = _SIGNAL_GROUPS["dependency keywords"]
    return any(marker in msg for marker in markers)

if has_dependency_language(normalized_message):
    score += DEPENDENCY_SCORING["Dependency keyword weight"]
    signals_found.append("dependency_keyword")
```

Do not copy the marker strings or semantic pattern inventory into Python.

### Pattern 3: Conversation History Context

Use recent message context to amplify confidence:

```python
def recent_messages_show_pattern(messages: list) -> bool:
    """Check last 3 messages for consistent pattern."""
    user_messages = [m["content"] for m in messages[-3:] if m.get("role") == "user"]
    return len([m for m in user_messages if has_signal(m)]) >= 2

if recent_messages_show_pattern(messages):
    score += 30
    signals_found.append("pattern_in_history")
```

## Threshold Management

Thresholds define when a detector's score triggers a framework override.

Semantic signal phrases, regex patterns, and qualitative response guidance belong in the
registered Markdown source. Executable scoring weights, thresholds, numeric ceilings,
recency multipliers, and routing priorities belong in Python-owned runtime configuration
under `src/soulmap/runtime/knowledge/runtime_config.py`.

Before tuning a detector, inspect its Python configuration, loader, tests, and evals.
Do not add numeric scoring values to Markdown or duplicate a Python-owned value in a
Markdown table. Update Markdown only when the semantic signals or qualitative guidance
change.

### Tune thresholds based on evals

1. Run `uv run soulmap eval-groups` to see which tests fail
2. If detector scores are too high or low, adjust the relevant Python-owned runtime configuration value and its validation tests
3. Re-run evals to verify the fix
4. Keep Markdown focused on the meaning of the signal and the response guidance; record executable configuration rationale alongside the Python configuration and tests

## Scoring best practices

### Combine multiple signals

Don't rely on a single keyword. Combine patterns:

```python
score = 0

# Weak signal: keyword match
if keyword_found:
    score += 10

# Medium signal: semantic structure
if structure_matches:
    score += 20

# Strong signal: confirmed by history
if history_confirms:
    score += 30

score = min(score, 100)  # Cap at 100
```

### Handle edge cases

```python
# No input: preserve this detector's documented no-input result.
if not messages:
    return detector_specific_no_input_result()

# Malformed entries: use the existing input validator where the detector contract
# requires a validated message history.
for msg in messages:
    if not isinstance(msg, dict) or "content" not in msg:
        continue
```

There is no universal `NO_DATA` result contract. Preserve the closest detector's
actual behavior and test its exact return shape.

## Integration with Framework Selector

A new ordinary framework detector has more than one integration point. Inspect the
current code and follow `.claude/rules/detector-development.md` before editing.

- Add the detector import and execution at the correct phase in
  `src/soulmap/runtime/routing/framework_selector.py`.
- Add its semantic binding to `_PRIMARY_DETECTOR_BINDINGS` or the relevant secondary
  binding; do not duplicate signal phrases in Python.
- Keep priority guidance in `skills/meta/orchestration.md` and its executable
  counterpart in `ORCHESTRATION_CONFIG`.
- Put numeric weights and thresholds in `DETECTOR_CONFIG` when required.
- Register the canonical Markdown source through the runtime registry when it is
  consumed by the detector.
- Add the required framework-template mapping and source-backed eval coverage.

Crisis detection and its independent safety-gate recheck are protected paths. Do not
copy, reorder, bypass, or edit the crisis branch when adding an ordinary detector.
Preserve the existing safety short-circuits and selector phases.

## Testing your detector

### Unit Tests

```python
# tests/unit/test_your_detector.py
from soulmap.runtime.detectors import your_detector

def test_detects_signal():
    messages = [{"role": "user", "content": "[signal text here]"}]
    result = your_detector.<detector_callable>(messages)
    assert result["level"] == "<detector-specific-high-level>"
    assert "expected_signal_name" in result["signals"]

def test_no_false_positives():
    messages = [{"role": "user", "content": "What's the weather?"}]
    result = your_detector.<detector_callable>(messages)
    assert result["level"] == "<detector-specific-no-signal-level>"

def test_no_input():
    result = your_detector.<detector_callable>([])
    assert result == <detector-specific-no-input-result>
```

### Integration Tests via Evals

Add test cases to `evals/datasets/groups.json` that should trigger your detector:

```json
{
  "g": "Your Framework, Core Signal",
  "cat": "your_cat",
  "sources": ["skills/frameworks/your_framework.md"],
  "items": [
    {
      "t": "input that triggers your detector",
      "expect_primary_framework": "YOUR_FRAMEWORK"
    }
  ]
}
```

Then run:

```bash
uv run soulmap eval-groups
```

Verify your detector's test cases pass.

## Message Normalization

Always normalize messages before pattern matching:

```python
from soulmap.runtime.io.text_normalization import normalize_message_text

for msg in user_messages:
    normalized = normalize_message_text(msg)
    # Now search normalized message for patterns
    if pattern.search(normalized):
        score += 10
```

This ensures consistent handling of quotes, whitespace, and common text variations.

## CLI Testing

Test your detector from the command line:

```bash
echo '{"messages": [{"role": "user", "content": "test input"}]}' | python -m soulmap.runtime.detectors.your_detector
```

Expected output shape is detector-specific. For a detector that exposes these fields, it may look like:

```json
{
  "level": "<detector-specific-level>",
  "signals": ["signal_name"],
  "recommendation": "..."
}
```

Do not assume every detector exposes a score or recommendation.

## Performance Considerations

- Pre-compile regex patterns (do not recompile in loops)
- Use efficient string operations (`.lower()` once, not per pattern)
- Bound history analysis only when the detector's existing contract permits it; preserve detectors that intentionally inspect full conversation history
- Avoid expensive operations in scoring loops

Example:

```python
# Good: normalize once
normalized_messages = [normalize_message_text(m) for m in user_messages]
for norm_msg in normalized_messages:
    for pattern_name, pattern in PATTERNS:
        if pattern.search(norm_msg):  # Fast lookup
            score += 10
```

## Workflow

1. Read `.claude/rules/detector-development.md` before writing any code.
2. Read the detector's registered Markdown source for semantic signals and qualitative guidance; read Python runtime configuration for executable weights and thresholds.
3. Inspect the closest existing detector and its tests. Preserve its callable, input, output, and CLI contracts rather than inventing a universal interface.
4. Keep semantic phrases and regex expressions in Markdown; keep executable scoring, thresholds, and routing configuration in Python.
5. Integrate the ordinary detector through the current selector phase, semantic binding, orchestration configuration, and source registry as applicable. Do not edit protected crisis paths.
6. Add source-backed eval cases to `evals/datasets/groups.json` using [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md).
7. Run `uv run soulmap test -n auto -q` and `uv run soulmap eval-groups` before pushing.

## Definition of done

A detector is done when:

- It preserves the detector-specific return contract established by the implementation and tests
- Semantic signals and qualitative guidance remain in Markdown; executable scoring weights, thresholds, and routing settings remain in Python-owned configuration
- It is called at the correct priority in `src/soulmap/runtime/routing/framework_selector.py`
- At least one eval case in `evals/datasets/groups.json` covers its primary signal
- `uv run soulmap test -n auto -q` passes with no regressions
- `uv run soulmap eval-groups` passes for all groups it affects

## Relationship to other skills

- **framework-author** defines what signals activate a framework → you implement detectors to identify those signals
- **eval-suite-maintainer** writes test cases → you tune your detector to pass those tests
- **research-and-gap-analysis** finds missing signals → you implement detectors to address those gaps
