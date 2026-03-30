#!/usr/bin/env bash
# Pre-tool hook intent: block any git push that targets main directly.
# Keeps the same branch workflow protection as the Claude local layer.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    raise SystemExit(0)

tool_input = data.get("tool_input", {})
if isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
    print(tool_input["command"])
    raise SystemExit(0)

tool_name = data.get("toolName")
tool_args = data.get("toolArgs")
if tool_name == "bash" and isinstance(tool_args, str):
    try:
        parsed = json.loads(tool_args)
    except Exception:
        print(tool_args)
    else:
        print(parsed.get("command", "") if isinstance(parsed, dict) else "")
else:
    print("")
' 2>/dev/null || echo "")

if echo "$COMMAND" | grep -qE "git push.*(origin\s+main|--force.*main|main\s*$)"; then
  echo "Blocked: direct push to 'main' is not allowed." >&2
  echo "Create a branch and push that instead:" >&2
  echo "  git checkout -b fix/your-change" >&2
  echo "  git push origin fix/your-change" >&2
  echo "See .agents/rules/git-and-release.md for the branch workflow." >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE "^git push(\s+origin)?\s*$"; then
  REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"
  CURRENT_BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "")
  if [[ "$CURRENT_BRANCH" == "main" ]]; then
    echo "Blocked: you are on 'main' and 'git push' would push to main." >&2
    echo "Switch to a feature branch first:" >&2
    echo "  git checkout -b fix/your-change" >&2
    echo "See .agents/rules/git-and-release.md for the branch workflow." >&2
    exit 2
  fi
fi

exit 0
