#!/usr/bin/env bash
# Post-edit hook intent: validate the eval dataset that was edited.
# Non-blocking. Emits the corresponding runner output to the agent.

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

case "$FILE_PATH" in
  */evals/datasets/groups.json|evals/datasets/groups.json)
    DATASET_FILE="groups.json"
    VALIDATOR=(uv run soulmap eval-groups)
    ;;
  */evals/datasets/markdown_contract_cases.json|evals/datasets/markdown_contract_cases.json)
    DATASET_FILE="markdown_contract_cases.json"
    VALIDATOR=(uv run soulmap eval-markdown-contracts)
    ;;
  */evals/datasets/response_generation_cases.json|evals/datasets/response_generation_cases.json)
    DATASET_FILE="response_generation_cases.json"
    VALIDATOR=(uv run soulmap eval-responses)
    ;;
  */evals/datasets/response_quality_cases.json|evals/datasets/response_quality_cases.json)
    DATASET_FILE="response_quality_cases.json"
    VALIDATOR=(uv run soulmap eval-response-quality)
    ;;
  */evals/datasets/safety_test_cases.json|evals/datasets/safety_test_cases.json)
    DATASET_FILE="safety_test_cases.json"
    VALIDATOR=(uv run python tests/eval_regression/test_safety_evals.py)
    ;;
  *)
    exit 0
    ;;
esac

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

cd "$REPO_ROOT"

TARGET_FILE="$REPO_ROOT/evals/datasets/$DATASET_FILE"
echo "[hook:post-edit-evals] Validating $TARGET_FILE" >&2

if ! python3 -c 'import json, sys; json.load(open(sys.argv[1], encoding="utf-8"))' "$TARGET_FILE" 2>/dev/null; then
  echo "[hook:post-edit-evals] JSON syntax error in $TARGET_FILE" >&2
  echo "JSON syntax error in $TARGET_FILE. Check for missing commas, unclosed braces/brackets, trailing commas, and duplicate field names."
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

markdown_eval_has_failures() {
  local output="$1"

  python3 -c '
import json
import sys

try:
    payload = json.loads(sys.stdin.read())
except Exception:
    raise SystemExit(1)

ok = payload.get("ok")
if ok is False:
    raise SystemExit(0)

summary = payload.get("summary")
if isinstance(summary, dict) and summary.get("failed_checks", 0):
    raise SystemExit(0)

raise SystemExit(1)
' <<<"$output"
}

if OUTPUT=$(run_eval_command "${VALIDATOR[@]}"); then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi

if [[ "$DATASET_FILE" == "markdown_contract_cases.json" ]] && markdown_eval_has_failures "$OUTPUT"; then
  EXIT_CODE=1
fi

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-evals] Validation issues detected in $TARGET_FILE" >&2
  echo "$OUTPUT" >&2
  echo "Validation issues detected in $TARGET_FILE:"
  echo "$OUTPUT"
else
  echo "[hook:post-edit-evals] Validation command completed for $DATASET_FILE." >&2
fi

exit 0
