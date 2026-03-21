#!/usr/bin/env bash
# PostToolUse hook: run markdown_contract after editing skills/ or templates/ .md files.
# Catches broken links, missing frontmatter, banned unicode early.
# Exit 0 always (non-blocking)  -  errors are reported to Claude as feedback.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Only act on .md files inside skills/ or templates/
if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

if [[ "$FILE_PATH" != *"/skills/"* ]] && [[ "$FILE_PATH" != *"/templates/"* ]]; then
  exit 0
fi

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}"

cd "$REPO_ROOT"

echo "[hook:post-edit-markdown] Checking markdown contract for $FILE_PATH" >&2

# Run the repo's markdown contract checker against just this file
OUTPUT=$(python3 -m modules.markdown_contract --root "$REPO_ROOT" 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-markdown] Contract violations found:" >&2
  echo "$OUTPUT" >&2
  # Write to stdout so Claude sees the feedback and can fix it
  echo "Markdown contract violations detected after editing $FILE_PATH:"
  echo "$OUTPUT"
fi

exit 0
