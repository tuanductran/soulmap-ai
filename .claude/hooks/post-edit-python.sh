#!/usr/bin/env bash
# Post-edit hook intent: format and lint a touched Python file.
# Non-blocking. Uses repo tooling if available.

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

if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

case "$FILE_PATH" in
  *"/src/"*|src/*.py|*"/tests/"*.py|tests/*.py|*"/scripts/"*.py|scripts/*.py) ;;
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

uv run ruff check --fix "$TARGET_FILE" 2>&1 || true
uv run ruff format "$TARGET_FILE" 2>&1 || true

exit 0
