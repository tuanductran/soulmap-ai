#!/usr/bin/env bash
# Post-edit hook intent: run pytest on the edited test file after saving.
# Non-blocking. Fast feedback only for the touched test file.

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
  *"/tests/"*.py|tests/*.py) ;;
  *) exit 0 ;;
esac

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

cd "$REPO_ROOT"

case "$FILE_PATH" in
  "$REPO_ROOT"/*) TARGET_FILE="$FILE_PATH" ;;
  *) TARGET_FILE="$REPO_ROOT/$FILE_PATH" ;;
esac

if [[ ! -f "$TARGET_FILE" ]]; then
  exit 0
fi

run_test_command() {
  local output
  local exit_code

  set +e
  output=$("$@" 2>&1)
  exit_code=$?
  set -e

  printf '%s' "$output"
  return "$exit_code"
}

if OUTPUT=$(run_test_command uv run soulmap test "$TARGET_FILE" --tb=short); then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-tests] Tests failed for $TARGET_FILE" >&2
  echo "$OUTPUT" >&2
  echo "Test failures in $TARGET_FILE after edit:"
  echo "$OUTPUT"
else
  echo "[hook:post-edit-tests] All tests passed." >&2
fi

exit 0
