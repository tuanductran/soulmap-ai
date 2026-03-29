#!/usr/bin/env bash
# Post-edit hook intent: validate evals/groups.json after edits.
# Non-blocking. Emits feedback if schema or evals fail.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    raise SystemExit(0)

tool_input = data.get("tool_input", {})
if isinstance(tool_input, dict) and isinstance(tool_input.get("file_path"), str):
    print(tool_input["file_path"])
    raise SystemExit(0)

tool_name = data.get("toolName")
tool_args = data.get("toolArgs")
if tool_name in {"edit", "create"} and isinstance(tool_args, str):
    try:
        parsed = json.loads(tool_args)
    except Exception:
        print("")
    else:
        print(parsed.get("path", "") if isinstance(parsed, dict) else "")
else:
    print("")
' 2>/dev/null || echo "")

if [[ "$FILE_PATH" != *"evals/groups.json" ]]; then
  exit 0
fi

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

cd "$REPO_ROOT"

echo "[hook:post-edit-evals] Validating $FILE_PATH" >&2

if ! python3 -c "import json; json.load(open('evals/groups.json'))" 2>/dev/null; then
  echo "[hook:post-edit-evals] JSON syntax error in evals/groups.json" >&2
  echo "JSON syntax error in evals/groups.json. Check for:"
  echo "  - Missing commas between items"
  echo "  - Unclosed braces or brackets"
  echo "  - Trailing commas after the last item"
  echo "  - Duplicate field names"
  exit 0
fi

if [[ -f "tools/eval_groups.py" ]] || python3 -c "import tools.eval_groups" 2>/dev/null; then
  OUTPUT=$(python -m tools.eval_groups 2>&1 || true)
  EXIT_CODE=$?

  if [[ $EXIT_CODE -ne 0 ]] || echo "$OUTPUT" | grep -q "FAIL\|ERROR"; then
    echo "[hook:post-edit-evals] Eval issues detected:" >&2
    echo "$OUTPUT" >&2
    echo "Eval validation issues detected in evals/groups.json:"
    echo "$OUTPUT"
  else
    echo "[hook:post-edit-evals] All evals passed." >&2
  fi
fi

if python tests/test_safety_evals.py >/dev/null 2>&1; then
  echo "[hook:post-edit-evals] Safety eval script passed." >&2
else
  echo "[hook:post-edit-evals] Safety eval script not available or failed." >&2
fi

exit 0
