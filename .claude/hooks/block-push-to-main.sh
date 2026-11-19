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

MAIN_PUSH_PATTERN="git([[:space:]]+-C[[:space:]]+('[^']+'|\"[^\"]+\"|[^[:space:]]+))?[[:space:]]+push.*([[:space:]]|:)(refs/heads/)?main([[:space:]]|$)"
if echo "$COMMAND" | grep -qE "$MAIN_PUSH_PATTERN"; then
  echo "Blocked: direct push to 'main' is not allowed." >&2
  echo "Create a branch and push that instead:" >&2
  echo "  git checkout -b fix/your-change" >&2
  echo "  git push origin fix/your-change" >&2
  echo "See .claude/rules/git-and-release.md for the branch workflow." >&2
  exit 2
fi

# A push without an explicit refspec uses the current branch's configured push
# destination. Resolve git -C so the check applies to the repository actually
# targeted by the command, not merely the project that owns this hook.
IMPLICIT_PUSH_PATTERN="git([[:space:]]+-C[[:space:]]+('[^']+'|\"[^\"]+\"|[^[:space:]]+))?[[:space:]]+push([[:space:]]+(-u|--set-upstream|--porcelain|--atomic|--dry-run|--no-verify|--force|--force-with-lease))*([[:space:]]+[^[:space:]]+)?[[:space:]]*$"
if echo "$COMMAND" | grep -qE "$IMPLICIT_PUSH_PATTERN"; then
  REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"
  PUSH_REPO_ROOT=$(printf '%s' "$COMMAND" | python3 -c '
import os, shlex, sys
try:
    tokens = shlex.split(sys.stdin.read())
except ValueError:
    print("")
    raise SystemExit(0)

for index, token in enumerate(tokens):
    if os.path.basename(token) != "git":
        continue
    cursor = index + 1
    repo = ""
    while cursor < len(tokens):
        current = tokens[cursor]
        if current == "-C" and cursor + 1 < len(tokens):
            repo = tokens[cursor + 1]
            cursor += 2
        elif current == "-c" and cursor + 1 < len(tokens):
            cursor += 2
        elif current.startswith("-"):
            cursor += 1
        else:
            break
    if cursor < len(tokens) and tokens[cursor] == "push":
        print(repo)
        break
' 2>/dev/null || echo "")
  PUSH_REPO_ROOT="${PUSH_REPO_ROOT:-$REPO_ROOT}"
  CURRENT_BRANCH=$(git -C "$PUSH_REPO_ROOT" branch --show-current 2>/dev/null || echo "")
  PUSH_BRANCH=$(git -C "$PUSH_REPO_ROOT" rev-parse --abbrev-ref --symbolic-full-name '@{push}' 2>/dev/null || echo "")

  if [[ "$CURRENT_BRANCH" == "main" || "$PUSH_BRANCH" == "main" || "$PUSH_BRANCH" == */main ]]; then
    echo "Blocked: this push would publish from or target the protected 'main' branch." >&2
    echo "Switch to a feature branch and push that instead." >&2
    echo "See .claude/rules/git-and-release.md for the branch workflow." >&2
    exit 2
  fi
fi

exit 0
