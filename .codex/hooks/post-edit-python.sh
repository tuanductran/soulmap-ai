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

if [[ "$FILE_PATH" != *"/modules/"* ]] && \
   [[ "$FILE_PATH" != *"/tools/"* ]] && \
   [[ "$FILE_PATH" != *"/tests/"* ]] && \
   [[ "$FILE_PATH" != *"/scripts/"* ]]; then
  exit 0
fi

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

cd "$REPO_ROOT"

python -m ruff format "$FILE_PATH" 2>&1 || true
python -m ruff check --fix "$FILE_PATH" 2>&1 || true
python -m isort "$FILE_PATH" 2>&1 || true

exit 0
