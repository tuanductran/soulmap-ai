#!/usr/bin/env bash
# PostToolUse hook: run markdown_contract after editing repo Markdown files.
# Catches broken links, missing frontmatter, and banned unicode early, including
# release-facing files such as CHANGELOG.md.
# Exit 0 always (non-blocking)  -  errors are reported to Claude as feedback.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Only act on Markdown files.
if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Ignore Markdown files outside the current repo root.
case "$FILE_PATH" in
  "$REPO_ROOT"/*) ;;
  *) exit 0 ;;
esac

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
