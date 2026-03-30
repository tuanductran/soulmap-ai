#!/usr/bin/env bash
# Post-edit hook intent: validate eval datasets after edits.
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

if [[ "$FILE_PATH" != *"evals/datasets/groups.json" ]] && [[ "$FILE_PATH" != *"evals/datasets/markdown_contract_cases.json" ]]; then
  exit 0
fi

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

cd "$REPO_ROOT"

echo "[hook:post-edit-evals] Validating $FILE_PATH" >&2

TARGET_FILE="evals/datasets/groups.json"
if [[ "$FILE_PATH" == *"evals/datasets/markdown_contract_cases.json" ]]; then
  TARGET_FILE="evals/datasets/markdown_contract_cases.json"
fi

if ! python3 -c "import json; json.load(open('$TARGET_FILE'))" 2>/dev/null; then
  echo "[hook:post-edit-evals] JSON syntax error in $TARGET_FILE" >&2
  echo "JSON syntax error in $TARGET_FILE. Check for:"
  echo "  - Missing commas between items"
  echo "  - Unclosed braces or brackets"
  echo "  - Trailing commas after the last item"
  echo "  - Duplicate field names"
  exit 0
fi

run_eval_command() {
  local output
  local exit_code

  set +e
  output=$("$@" 2>&1)
  exit_code=$?
  set -e

  printf '%s' "$output"
  return "$exit_code"
}

if [[ "$TARGET_FILE" == "evals/datasets/groups.json" ]] && ([[ -f "src/soulmap_devtools/evals/eval_groups.py" ]] || python3 -c "import soulmap_devtools.evals.eval_groups" 2>/dev/null); then
  if OUTPUT=$(run_eval_command python -m soulmap_devtools.cli.eval_groups); then
    EXIT_CODE=0
  else
    EXIT_CODE=$?
  fi

  if [[ $EXIT_CODE -ne 0 ]] || echo "$OUTPUT" | grep -q "FAIL\|ERROR"; then
    echo "[hook:post-edit-evals] Eval issues detected:" >&2
    echo "$OUTPUT" >&2
    echo "Eval validation issues detected in evals/datasets/groups.json:"
    echo "$OUTPUT"
  else
    echo "[hook:post-edit-evals] All evals passed." >&2
  fi
fi

if [[ "$TARGET_FILE" == "evals/datasets/markdown_contract_cases.json" ]] && ([[ -f "src/soulmap_devtools/evals/eval_markdown_contracts.py" ]] || python3 -c "import soulmap_devtools.evals.eval_markdown_contracts" 2>/dev/null); then
  if OUTPUT=$(run_eval_command python -m soulmap_devtools.cli.eval_markdown_contracts); then
    EXIT_CODE=0
  else
    EXIT_CODE=$?
  fi

  if [[ $EXIT_CODE -ne 0 ]] || echo "$OUTPUT" | grep -q "failed_checks"; then
    echo "[hook:post-edit-evals] Markdown contract issues detected:" >&2
    echo "$OUTPUT" >&2
    echo "Markdown contract issues detected in evals/datasets/markdown_contract_cases.json:"
    echo "$OUTPUT"
  else
    echo "[hook:post-edit-evals] Markdown contract eval passed." >&2
  fi
fi

if python tests/eval_regression/test_safety_evals.py >/dev/null 2>&1; then
  echo "[hook:post-edit-evals] Safety eval script passed." >&2
else
  echo "[hook:post-edit-evals] Safety eval script not available or failed." >&2
fi

exit 0
