#!/usr/bin/env bash
# PostToolUse hook: validate evals/groups.json and run eval suite after editing.
# Fires on Write and Edit tool calls that target evals/groups.json.
# Exit 0 = proceed. Provides validation feedback but does not block.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Only act on evals/groups.json
if [[ "$FILE_PATH" != *"evals/groups.json" ]]; then
  exit 0
fi

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}"

cd "$REPO_ROOT"

echo "[hook:post-edit-evals] Validating $FILE_PATH" >&2

# 1. Check JSON syntax
if ! python3 -c "import json; json.load(open('evals/groups.json'))" 2>/dev/null; then
  echo "[hook:post-edit-evals] ✗ JSON syntax error in evals/groups.json" >&2
  echo "JSON syntax error in evals/groups.json. Check for:"
  echo "  - Missing commas between items"
  echo "  - Unclosed braces or brackets"
  echo "  - Trailing commas after the last item"
  echo "  - Duplicate field names"
  exit 0
fi

echo "[hook:post-edit-evals] ✓ JSON syntax valid" >&2

# 2. Validate against schema and run eval_groups if available
if [[ -f "modules/tools/eval_groups.py" ]] || python3 -c "from soulmap_ai.tools import eval_groups" 2>/dev/null; then
  echo "[hook:post-edit-evals] Running eval_groups validation..." >&2
  
  OUTPUT=$(python3 -m soulmap_ai.tools.eval_groups 2>&1 || true)
  EXIT_CODE=$?
  
  if [[ $EXIT_CODE -ne 0 ]] || echo "$OUTPUT" | grep -q "FAIL\|ERROR"; then
    echo "[hook:post-edit-evals] ⚠ Eval issues detected:" >&2
    echo "$OUTPUT" >&2
    echo ""
    echo "Eval validation issues detected in evals/groups.json:"
    echo "$OUTPUT"
  else
    echo "[hook:post-edit-evals] ✓ All evals passed" >&2
  fi
else
  echo "[hook:post-edit-evals] eval_groups tool not found; skipping full validation" >&2
fi

# 3. Run schema-focused unit tests if available
if python3 -m pytest tests/test_safety_evals.py -q 2>/dev/null; then
  echo "[hook:post-edit-evals] ✓ Schema tests passed" >&2
else
  echo "[hook:post-edit-evals] Schema tests not available or failed" >&2
fi

exit 0
