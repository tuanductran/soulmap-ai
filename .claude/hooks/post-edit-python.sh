#!/usr/bin/env bash
# PostToolUse hook: auto-format and lint after editing a Python file.
# Fires on Write and Edit tool calls that target *.py files.
# Exit 0 = proceed. Errors are logged but do not block Claude.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Only act on Python files in the project source directories
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

if [[ "$FILE_PATH" != *"/modules/"* ]] && \
   [[ "$FILE_PATH" != *"/tools/"* ]] && \
   [[ "$FILE_PATH" != *"/tests/"* ]] && \
   [[ "$FILE_PATH" != *"/scripts/"* ]]; then
  exit 0
fi

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}"

cd "$REPO_ROOT"

echo "[hook:post-edit-python] Formatting $FILE_PATH" >&2

# 1. ruff format (auto-fix style)
python3 -m ruff format "$FILE_PATH" 2>&1 || true

# 2. ruff check with auto-fix (lint violations)
python3 -m ruff check --fix "$FILE_PATH" 2>&1 || true

# 3. isort (import order)
python3 -m isort "$FILE_PATH" 2>&1 || true

echo "[hook:post-edit-python] Done." >&2
exit 0
