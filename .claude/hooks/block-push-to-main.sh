#!/usr/bin/env bash
# PreToolUse hook: block any git push that targets main directly.
# Enforces the branch workflow rule from .claude/rules/git-and-release.md.
# Exit 2 = block the command and send feedback to Claude.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# Match: git push [remote] main  OR  git push --follow-tags (when on main)
# Allow: git push origin <branch> where branch != main
if echo "$COMMAND" | grep -qE "git push.*(origin\s+main|--force.*main|main\s*$)"; then
  echo "Blocked: direct push to 'main' is not allowed." >&2
  echo "Create a branch and push that instead:" >&2
  echo "  git checkout -b fix/your-change" >&2
  echo "  git push origin fix/your-change" >&2
  echo "See .claude/rules/git-and-release.md for the branch workflow." >&2
  exit 2
fi

# Also block: git push without specifying a branch when currently on main
if echo "$COMMAND" | grep -qE "^git push(\s+origin)?\s*$"; then
  REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
  CURRENT_BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "")
  if [[ "$CURRENT_BRANCH" == "main" ]]; then
    echo "Blocked: you are on 'main' and 'git push' would push to main." >&2
    echo "Switch to a feature branch first:" >&2
    echo "  git checkout -b fix/your-change" >&2
    echo "See .claude/rules/git-and-release.md for the branch workflow." >&2
    exit 2
  fi
fi

exit 0
