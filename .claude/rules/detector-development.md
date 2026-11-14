---
paths:
  - src/soulmap/runtime/detectors/*_detector.py
  - src/soulmap/runtime/knowledge/runtime_config.py
  - tests/unit/test_*_detector.py
---

# Detector development rules

Use these conventions when writing or extending Python detector modules.

## Module structure

Detector modules should follow the established local pattern, but the public callable,
input shape, and result semantics are detector-specific. Use the closest current,
non-safety detector as the template rather than imposing a universal interface.

For example, dependency detection exposes `analyze_dependency()` and returns
dependency-specific levels. Other detectors may return a different structure. Crisis
detection is a protected safety path and is not a template for ordinary detector work.

A common CLI shape is:

```python
"""Brief description of what this detector scores."""

from __future__ import annotations

import json
import re
import sys

from soulmap.runtime.io.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from soulmap.runtime.knowledge.runtime_config import (
    CONFIG_CONSTANT_NAME,
    ANOTHER_CONFIG_CONSTANT,
)

HistoryMessage = dict[str, str]


def analyze_dependency(conversation_messages: list) -> dict:
    """
    Main detection function.

    Args:
        conversation_messages: List of dicts with 'role' and 'content' keys.

    Returns:
        Dict with keys: level (str), score (int), signals (list), recommendation (str)
    """
    # Implementation here
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

**Rules**:

- Start with docstring describing purpose
- Use `from __future__ import annotations` for forward compatibility
- Import from `soulmap.runtime.io.cli_payload` for stdin/stdout handling
- Read the current detector and its tests before choosing imports, payload helpers,
  types, or a public callable; the example above is illustrative, not a required
  module template.
- Import Python-owned executable policy from
  `soulmap.runtime.knowledge.runtime_config` only when the detector needs it.
- Use the repository's established message/history types and validation helpers
  rather than introducing a parallel payload contract.
- Name the public function for its actual behavior, for example
  `analyze_dependency` or `detect_grief`.

## Scoring methods

Detectors commonly expose a dict containing fields such as `level`, `score`, `signals`, and `recommendation`, but these are not a universal enum or schema. Preserve the existing detector's output contract and tests when extending it.

| Key | Type | Description |
|-----|------|-------------|
| `level` | str | Detector-specific classification; do not assume a repo-wide enum |
| `score` | int | Detector-specific numeric score; preserve the existing detector's scoring convention |
| `signals` | list | List of signal descriptions found, for example `["only_you_understand_me"]` |
| `recommendation` | str | Plain English recommendation for the framework or action |

Example return value:

```python
{
    "level": "HIGH_DEPENDENCY",
    "score": 2,
    "signals": ["dependency_keyword"],
    "recommendation": "User shows dependency signals. Use the detector-specific dependency response contract."
}
```

## Threshold and scoring ownership

The repository contract assigns executable thresholds, weights, numeric ceilings,
recency values, and routing tables to Python-owned runtime configuration in
`src/soulmap/runtime/knowledge/runtime_config.py`. Markdown remains the canonical
source for semantic signals, qualitative guidance, and user-facing behavioral meaning.

When changing executable policy, update the corresponding Python configuration and
its validation tests. When changing semantic signals or qualitative guidance, update
the registered Markdown source and its contract tests. Do not create duplicate numeric
sources of truth in Markdown, and do not move semantic knowledge into Python merely
for stylistic consistency.

## Secondary scoring patterns

Some signals contribute partial scores. Use this pattern:

```python
_RULES = DETECTOR_CONFIG["your_detector"]
score = 0
signals_found = []

# Pattern 1: Keyword match (low confidence)
for pattern_name, pattern_regex in PATTERNS:
    if pattern_regex.search(msg):
        score += _RULES["Keyword match weight"]
        signals_found.append(pattern_name)

# Pattern 2: Semantic structure (medium confidence)
if has_structure_x(msg):
    score += _RULES["Semantic structure weight"]
    signals_found.append("structure_x_detected")

# Pattern 3: Context from history (high confidence)
if recent_messages_show_y():
    score += _RULES["History context weight"]
    signals_found.append("context_confirms_signal")

# Apply the configured score ceiling
score = min(score, _RULES["Maximum score"])
```

**Rules**:

- Combine multiple weak signals into a single higher confidence score
- Later signals can amplify or override earlier ones
- If a detector needs a score ceiling, define it in Python runtime configuration and apply that configured value; do not hardcode a generic maximum
- Document the weighting rationale in code comments

## Integration methods

### Framework selector integration

Do not add a detector by copying or editing the crisis branch. Crisis detection
and its independent safety-gate recheck are protected paths.

For a new ordinary framework detector, inspect the current integration points before
changing anything:

- the detector imports and execution phase in
  `src/soulmap/runtime/routing/framework_selector.py`
- the semantic framework binding in `_PRIMARY_DETECTOR_BINDINGS` (or the relevant
  secondary binding)
- the priority row in `skills/meta/orchestration.md` and its Python-owned executable
  counterpart in `ORCHESTRATION_CONFIG`
- numeric thresholds and weights in `DETECTOR_CONFIG`, when needed
- the canonical Markdown source and `source_registry.py` mapping when the detector
  loads knowledge from a registered skill section
- framework template mapping and routing/evaluation coverage, where applicable

Preserve the existing order of safety short-circuits and selector phases. Do not
introduce a second source of truth for priority, numeric policy, or semantic signals.

### CLI tool integration

Detectors can be run standalone via CLI:

```bash
echo '{"messages": [...]}' | python -m soulmap.runtime.detectors.dependency_detector
```

This works automatically if your module follows the `if __name__ == "__main__"` pattern.

### Test integration

Write unit tests in `tests/unit/test_YOUR_detector.py`:

```python
def test_analyzer_detects_signal():
    messages = [{"role": "user", "content": "only you understand me"}]
    result = analyze_dependency(messages)
    assert result["level"] == "HIGH_DEPENDENCY"
    assert "only_you_understand_me" in result["signals"]
```

## Pattern definitions

For knowledge-first detectors, semantic signal patterns belong in the detector's
canonical Markdown source. Python loads the labeled pattern rows, validates the
contract, and compiles them at module load time. Do not duplicate those patterns in
Python constants or configuration modules.

For implementation-only patterns used to parse or normalize text (rather than define
domain signals), module-level compiled regular expressions remain appropriate.

**Rules**:

- Keep domain signal labels and regex expressions together in the canonical knowledge source
- Compile loaded expressions once at module initialization
- Preserve normalization and matching semantics when changing a pattern
- Add regression cases for positive matches, exclusions, and whitespace/case variants
- Keep implementation-only parsing patterns separate from domain signal knowledge

## Message normalization

Always normalize user messages before pattern matching:

```python
from soulmap.runtime.io.text_normalization import normalize_message_text

for message in conversation_messages:
    if message.get("role") == "user":
        normalized = normalize_message_text(message["content"])
        # Now search normalized message
```

This handles quote standardization and whitespace cleanup consistently across all detectors.

## Testing and validation

### Unit tests

Write focused tests for each detector:

```python
def test_high_threshold():
    # Input that should exceed high threshold
    messages = [{"role": "user", "content": "..."}]
    result = <detector_callable>(messages)
    assert result["score"] >= HIGH_THRESHOLD

def test_no_signal():
    # Input with no relevant signal
    messages = [{"role": "user", "content": "What's the weather?"}]
    result = <detector_callable>(messages)
    assert result["level"] == "<detector-specific-no-signal-level>"
```

### Integration tests

Test your detector through the eval suite:

1. Add test cases to `evals/datasets/groups.json` with `expect_primary_framework` set to the framework your detector selects
2. Run `uv run soulmap eval-groups` to validate
3. Adjust thresholds if eval cases fail unexpectedly

## Error handling

Detectors must handle malformed input gracefully:

```python
if not conversation_messages:
    return {
        "level": "NO_DATA",
        "score": 0,
        "signals": [],
        "recommendation": "No messages to analyze."
    }

user_messages = [
    m["content"] for m in conversation_messages
    if isinstance(m, dict) and m.get("role") == "user"
]

if not user_messages:
    return {
        "level": "NO_DATA",
        "score": 0,
        "signals": [],
        "recommendation": "No user messages found."
    }
```

**Rules**:

- Preserve the detector's established result contract and handle malformed input gracefully
- Use `print_json_error()` for CLI error payloads when the module exposes a CLI.
- Preserve detector-specific no-input behavior rather than imposing a universal level.
- Test malformed inputs and boundary cases covered by the detector's contract.
