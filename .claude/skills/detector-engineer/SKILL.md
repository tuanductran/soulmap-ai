---
name: detector-engineer
description: Build and maintain Python detector modules that identify framework selection signals in conversation history.
---

# Detector Engineer

Use this skill when writing new detector modules, extending existing detectors, or tuning detector thresholds based on eval results.

## Do not use this skill for

- Editing rules and conventions, refer to [`../rules/detector-development.md`](../../rules/detector-development.md)
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

Every detector has this structure:

```python
"""Score conversation history for signs of [signal]."""

import json
import sys
from soulmap.runtime.io.cli_payload import read_stdin_json, print_json_error
from soulmap.runtime.config import THRESHOLD_CONSTANTS

def analyze_signal(conversation_messages: list) -> dict:
    """Main scoring function."""
    # Implementation
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

## Return value contract

Every detector returns a standardized dict:

```python
{
    "level": "HIGH",              # Signal level: TIER_1, HIGH, MODERATE, LOW, NONE, NO_DATA
    "score": 75,                  # Numeric score (0-100 for consistency)
    "signals": ["signal_name"],   # List of signal descriptions found
    "recommendation": "..."       # Plain English recommendation
}
```

**Levels**:

- `TIER_1`, Highest severity (crisis, immediate danger)
- `HIGH`, Strong signals requiring framework override
- `MODERATE`, Notable signals worth attention
- `LOW`, Weak signals, may be context-dependent
- `NONE`, No signals found
- `NO_DATA`, Insufficient input to analyze

## Signal detection patterns

### Pattern 1: Keyword and Regex Matching

Use pre-compiled regex patterns defined at module level:

```python
SIGNAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("signal_name", re.compile(r"pattern here", re.IGNORECASE)),
    ("another_signal", re.compile(r"another pattern", re.IGNORECASE)),
]

# In analyze function:
for pattern_name, pattern_regex in SIGNAL_PATTERNS:
    if pattern_regex.search(normalized_message):
        score += 10
        signals_found.append(pattern_name)
```

**Rules**:

- Pre-compile patterns at module load (not in functions)
- Use descriptive names for each pattern
- Use `re.IGNORECASE` for human input matching
- Store as tuple of (name, compiled_pattern)

### Pattern 2: Semantic Structure Analysis

Detect patterns in sentence structure or word order:

```python
def has_dependency_language(msg: str) -> bool:
    """Check for exclusive reliance language."""
    markers = ["only you", "no one else", "can't talk to anyone"]
    return any(marker in msg.lower() for marker in markers)

if has_dependency_language(msg):
    score += 20
    signals_found.append("exclusive_reliance")
```

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

### Define thresholds in `src/soulmap/runtime/config/`

```python
# src/soulmap/runtime/config/safety.py or src/soulmap/runtime/config/meaning.py
HIGH_DEPENDENCY_THRESHOLD = 50      # Score >= 50 triggers Dependency framework
MODERATE_DEPENDENCY_THRESHOLD = 25  # Score >= 25 warrants caution
CRISIS_SEVERITY_THRESHOLD = 80      # Immediate-crisis score
```

### Use thresholds consistently

```python
from soulmap.runtime.config import HIGH_DEPENDENCY_THRESHOLD

if score >= HIGH_DEPENDENCY_THRESHOLD:
    level = "HIGH"
elif score > 0:
    level = "MODERATE"
else:
    level = "NONE"
```

### Tune thresholds based on evals

1. Run `uv run soulmap eval-groups` to see which tests fail
2. If detector scores are too high or low, adjust the threshold in the relevant file under `src/soulmap/runtime/config/`
3. Re-run evals to verify the fix
4. Document threshold rationale in comments

Example adjustment:

```python
# Before: threshold too high, missing moderate dependency cases
HIGH_DEPENDENCY_THRESHOLD = 75  # Changed from 75 to 50
# Now: threshold captures high-confidence dependency signals
HIGH_DEPENDENCY_THRESHOLD = 50
```

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
# No input
if not messages:
    return {"level": "NO_DATA", "score": 0, "signals": [], "recommendation": "..."}

# Empty user messages
user_messages = [m["content"] for m in messages if m.get("role") == "user"]
if not user_messages:
    return {"level": "NO_DATA", "score": 0, "signals": [], "recommendation": "..."}

# Malformed entries
for msg in messages:
    if not isinstance(msg, dict) or "content" not in msg:
        continue
```

## Integration with Framework Selector

Your detector integrates here in `src/soulmap/runtime/routing/framework_selector.py`:

```python
from soulmap.runtime.detectors import your_detector

def select_framework(messages: list) -> str:
    # ... crisis check first (highest priority) ...

    # Your detector
    result = your_detector.analyze_signal(messages)
    if result["level"] == "HIGH":
        return "YOUR_FRAMEWORK"

    # ... continue with other detectors ...
```

**Rules**:

- Check detectors in priority order (defined in AGENTS.md Section 2)
- Higher-priority signals always override lower-priority ones
- Each detector should handle its own edge cases gracefully

## Testing your detector

### Unit Tests

```python
# tests/unit/test_your_detector.py
from soulmap.runtime.detectors import your_detector

def test_detects_signal():
    messages = [{"role": "user", "content": "[signal text here]"}]
    result = your_detector.analyze_signal(messages)
    assert result["level"] == "HIGH"
    assert "expected_signal_name" in result["signals"]

def test_no_false_positives():
    messages = [{"role": "user", "content": "What's the weather?"}]
    result = your_detector.analyze_signal(messages)
    assert result["level"] == "NONE"

def test_no_data():
    result = your_detector.analyze_signal([])
    assert result["level"] == "NO_DATA"
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

Expected output:

```json
{
  "level": "HIGH",
  "score": 75,
  "signals": ["signal_name"],
  "recommendation": "..."
}
```

## Performance Considerations

- Pre-compile regex patterns (do not recompile in loops)
- Use efficient string operations (`.lower()` once, not per pattern)
- Limit history analysis to recent messages (last 10, not entire history)
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

1. Read `../rules/detector-development.md` before writing any code.
2. Check `src/soulmap/runtime/config/` for existing signal phrase constants to extend rather than duplicate.
3. Write the detector following the anatomy and return value contract defined in this skill.
4. Add threshold constants to `src/soulmap/runtime/config/safety.py` or the appropriate domain config.
5. Integrate the detector call into `src/soulmap/runtime/routing/framework_selector.py` at the correct priority.
6. Add eval cases to `evals/datasets/groups.json` using [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md).
7. Run `uv run soulmap test -n auto -q` and `uv run soulmap eval-groups` before pushing.

## Definition of done

A detector is done when:

- It returns a dict matching the standard return value contract above
- All signal constants live in `src/soulmap/runtime/config/` not inline in the function
- It is called at the correct priority in `src/soulmap/runtime/routing/framework_selector.py`
- At least one eval case in `evals/datasets/groups.json` covers its primary signal
- `uv run soulmap test -n auto -q` passes with no regressions
- `uv run soulmap eval-groups` passes for all groups it affects

## Relationship to other skills

- **framework-author** defines what signals activate a framework → you implement detectors to identify those signals
- **eval-suite-maintainer** writes test cases → you tune your detector to pass those tests
- **research-and-gap-analysis** finds missing signals → you implement detectors to address those gaps
