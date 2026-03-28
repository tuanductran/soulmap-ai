---
paths:
  - modules/*_detector.py
  - modules/config.py
  - tests/test_*_detector.py
---

# Detector Development Rules

Use these conventions when writing or extending Python detector modules.

## Module Structure

Every detector module follows this structure:

```python
"""Brief description of what this detector scores."""

from __future__ import annotations

import json
import re
import sys

from modules.cli_payload import (
    print_json_error,
    read_stdin_json,
    require_message_history_fields,
)
from modules.config import (
    CONFIG_CONSTANT_NAME,
    ANOTHER_CONFIG_CONSTANT,
)

HistoryMessage = dict[str, str]


def analyze_signal(conversation_messages: list) -> dict:
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
        result = analyze_signal(payload.get("messages", []))
        print(json.dumps(result))
    except Exception as e:
        print_json_error(str(e))
        sys.exit(1)
```

**Rules**:

- Start with docstring describing purpose
- Use `from __future__ import annotations` for forward compatibility
- Import from `modules.cli_payload` for stdin/stdout handling
- Import config constants from `modules.config`
- Define type hints using `HistoryMessage = dict[str, str]`
- Name the main function descriptively (e.g., `analyze_dependency`, `detect_crisis`)

## Scoring Methods

Detectors return a standardized dict with four keys:

| Key | Type | Description |
|-----|------|-------------|
| `level` | str | Signal level: `"TIER_1"`, `"HIGH"`, `"MODERATE"`, `"LOW"`, `"NONE"`, `"NO_DATA"` |
| `score` | int | Numeric score (0-100 for consistency, or match threshold convention) |
| `signals` | list | List of signal descriptions found (e.g., `["only_you_understand_me"]`) |
| `recommendation` | str | Plain English recommendation for the framework or action |

Example return value:

```python
{
    "level": "HIGH",
    "score": 75,
    "signals": ["unhealthy_comparison", "isolation_language"],
    "recommendation": "User shows dependency signals. Use Dependency framework. Check for isolation."
}
```

## Threshold Conventions

Thresholds are defined in `modules/config.py` as named constants:

```python
HIGH_DEPENDENCY_THRESHOLD = 50
MODERATE_DEPENDENCY_THRESHOLD = 25
CRISIS_SEVERITY_THRESHOLD = 80
```

**Rules for thresholds**:

- Define all numeric thresholds as module-level constants in `config.py`
- Use semantic names (e.g., `HIGH_`, `MODERATE_`, `CRITICAL_`)
- Document the threshold purpose with a comment
- Use thresholds consistently across detectors
- Thresholds should be tuned through eval suite assertions (see `evals/groups.json`)

Example:

```python
# modules/config.py
HIGH_DEPENDENCY_THRESHOLD = 50  # Score >= 50 triggers Dependency framework
MODERATE_DEPENDENCY_THRESHOLD = 25  # Score >= 25 warrants dependency caution
```

## Secondary Scoring Patterns

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

## Integration Methods

### Framework Selector Integration

Add your detector to the framework selection chain in `modules/framework_selector.py`:

```python
def select_framework(conversation_messages: list) -> str:
    # ... existing priority checks ...
    
    # Your detector here
    crisis_result = crisis_detector.analyze_crisis(conversation_messages)
    if crisis_result["level"] == "TIER_1":
        return "CRISIS"
    
    # Continue with other detectors
```

### CLI Tool Integration

Detectors can be run standalone via CLI:

```bash
echo '{"messages": [...]}' | python3 -m modules.dependency_detector
```

This works automatically if your module follows the `if __name__ == "__main__"` pattern.

### Test Integration

Write unit tests in `tests/test_YOUR_detector.py`:

```python
def test_analyzer_detects_signal():
    messages = [{"role": "user", "content": "only you understand me"}]
    result = analyze_dependency(messages)
    assert result["level"] == "HIGH"
    assert "only_you_understand_me" in result["signals"]
```

## Pattern Definitions

Detectors use regex patterns to identify signals. Store pattern definitions at module level:

```python
DEPENDENCY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "only you understand me",
        re.compile(r"\bonly you\s+(?:really\s+)?understand(?:s)?\s+me\b", re.IGNORECASE),
    ),
    (
        "you're the only one",
        re.compile(r"\byou(?:'re| are)\s+the\s+only\s+one\b", re.IGNORECASE),
    ),
]
```

**Rules**:

- Use tuples of (name, compiled_pattern) for readability
- Pre-compile regex patterns at module load time
- Use `re.IGNORECASE` for case-insensitive matching
- Document what each pattern detects
- Keep patterns maintainable and not overly complex

## Message Normalization

Always normalize user messages before pattern matching:

```python
from modules.text_normalization import normalize_message_text

for message in conversation_messages:
    if message.get("role") == "user":
        normalized = normalize_message_text(message["content"])
        # Now search normalized message
```

This handles quote standardization and whitespace cleanup consistently across all detectors.

## Testing and Validation

### Unit Tests

Write focused tests for each detector:

```python
def test_high_threshold():
    # Input that should exceed high threshold
    messages = [{"role": "user", "content": "..."}]
    result = analyze_signal(messages)
    assert result["score"] >= HIGH_THRESHOLD

def test_no_signal():
    # Input with no relevant signal
    messages = [{"role": "user", "content": "What's the weather?"}]
    result = analyze_signal(messages)
    assert result["level"] == "NONE"
```

### Integration Tests

Test your detector through the eval suite:

1. Add test cases to `evals/groups.json` with `expect_primary_framework` set to the framework your detector selects
2. Run `python3 -m soulmap_ai.tools.eval_groups` to validate
3. Adjust thresholds if eval cases fail unexpectedly

## Error Handling

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

- Always return a valid result dict, never raise uncaught exceptions
- Use `print_json_error()` for error messages to stdout
- Return "NO_DATA" level when input is insufficient
- Test edge cases: empty lists, malformed objects, missing fields
