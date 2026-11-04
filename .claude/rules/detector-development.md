---
paths:
  - src/soulmap/runtime/detectors/*_detector.py
  - src/soulmap/runtime/knowledge/runtime_config.py
  - tests/unit/test_*_detector.py
---

# Detector development rules

Use these conventions when writing or extending Python detector modules.

## Module structure

Detector modules should follow the established local pattern, but the public callable and result semantics are detector-specific. Use the closest existing detector as the template rather than imposing a universal interface.\n\nFor example, dependency detection exposes `analyze_dependency()` and returns dependency-specific levels. Crisis detection has its own safety contract.\n\nA common CLI shape is:

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
- Import runtime policy from `soulmap.runtime.knowledge.runtime_config`
- Define type hints using `HistoryMessage = dict[str, str]`
- Name the main function descriptively, for example `analyze_dependency` or
  `detect_crisis`

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

## Threshold conventions

For knowledge-first detectors, the registered Markdown runtime source owns semantic
thresholds and scoring values. Python may parse, normalize, and enforce those values,
but must not create a parallel source of truth in `src/soulmap/runtime/config/`.

For example, dependency thresholds are defined in
`skills/safety/dependency-detection.md`. Update that canonical source, preserve its
runtime contract, and validate the change through the relevant eval suite.

Only use Python configuration constants when the existing architecture explicitly
assigns that value to runtime configuration; do not migrate Markdown-owned knowledge
into Python for stylistic consistency.

## Secondary scoring patterns

Some signals contribute partial scores. Use this pattern:

```python
score = 0
signals_found = []

# Pattern 1: Keyword match (low confidence)
for pattern_name, pattern_regex in PATTERNS:
    if pattern_regex.search(msg):
        score += 10
        signals_found.append(pattern_name)

# Pattern 2: Semantic structure (medium confidence)
if has_structure_x(msg):
    score += 20
    signals_found.append("structure_x_detected")

# Pattern 3: Context from history (high confidence)
if recent_messages_show_y():
    score += 30
    signals_found.append("context_confirms_signal")

# Cap at 100
score = min(score, 100)
```

**Rules**:

- Combine multiple weak signals into a single higher confidence score
- Later signals can amplify or override earlier ones
- Always cap the final score at a reasonable maximum (typically 100)
- Document the weighting rationale in code comments

## Integration methods

### Framework selector integration

Add your detector to the framework selection chain in
`src/soulmap/runtime/routing/framework_selector.py`:

```python
def select_framework(conversation_messages: list) -> str:
    # ... existing priority checks ...

    # Your detector here
    crisis_result = crisis_detector.<crisis_detector_callable>(conversation_messages)
    if <crisis-tier-1-condition>:
        return "CRISIS"

    # Continue with other detectors
```

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
- Use `print_json_error()` for error messages to stdout
- Return "NO_DATA" level when input is insufficient
- Test edge cases: empty lists, malformed objects, missing fields
