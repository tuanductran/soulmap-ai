#!/usr/bin/env bash
# PostToolUse hook: run pytest on the edited test file after saving.
# Runs only the specific test file to keep feedback fast.
# Exit 0 always (non-blocking).

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Only act on test files
if [[ "$FILE_PATH" != *"/tests/test_"*.py ]]; then
  exit 0
fi

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}"

cd "$REPO_ROOT"

echo "[hook:post-edit-tests] Running pytest on $FILE_PATH" >&2

OUTPUT=$(python3 -m pytest "$FILE_PATH" -q --tb=short 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-tests] Tests failed:" >&2
  echo "$OUTPUT" >&2
  echo "Test failures in $FILE_PATH after edit:"
  echo "$OUTPUT"
else
  echo "[hook:post-edit-tests] All tests passed." >&2
fi

exit 0
