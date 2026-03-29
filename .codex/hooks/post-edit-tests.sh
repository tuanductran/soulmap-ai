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

if [[ "$FILE_PATH" != *"/tests/test_"*.py ]]; then
  exit 0
fi

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

cd "$REPO_ROOT"

OUTPUT=$(python -m pytest "$FILE_PATH" -q --tb=short 2>&1 || true)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-tests] Tests failed for $FILE_PATH" >&2
  echo "$OUTPUT" >&2
  echo "Test failures in $FILE_PATH after edit:"
  echo "$OUTPUT"
else
  echo "[hook:post-edit-tests] All tests passed." >&2
fi

exit 0
