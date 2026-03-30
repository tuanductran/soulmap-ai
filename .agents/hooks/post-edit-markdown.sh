#!/usr/bin/env bash
# Post-edit hook intent: run markdown contract after editing repo Markdown files.
# Non-blocking. Reports violations to the agent.

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

if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

case "$FILE_PATH" in
  "$REPO_ROOT"/*) ;;
  *) exit 0 ;;
esac

cd "$REPO_ROOT"

run_contract_command() {
  local output
  local exit_code

  set +e
  output=$("$@" 2>&1)
  exit_code=$?
  set -e

  printf '%s' "$output"
  return "$exit_code"
}

if OUTPUT=$(run_contract_command python -m soulmap_runtime.guards.markdown_contract --root "$REPO_ROOT"); then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-markdown] Contract violations detected after editing $FILE_PATH" >&2
  echo "$OUTPUT" >&2
  echo "Markdown contract violations detected after editing $FILE_PATH:"
  echo "$OUTPUT"
fi

exit 0
