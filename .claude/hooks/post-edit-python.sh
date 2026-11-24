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

REPO_ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || pwd)}}"

# Resolve the edited path before invoking Ruff. A lexical prefix check is not
# sufficient: absolute paths and ../ segments can otherwise escape the repo.
TARGET_FILE=$(python3 - "$REPO_ROOT" "$FILE_PATH" <<'PY'
from pathlib import Path
import sys

try:
    repo_root = Path(sys.argv[1]).resolve(strict=True)
    candidate = Path(sys.argv[2])
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    target = candidate.resolve(strict=True)
    relative = target.relative_to(repo_root)
except (OSError, RuntimeError, ValueError):
    raise SystemExit(0)

if (
    not target.is_file()
    or target.suffix != ".py"
    or not relative.parts
    or relative.parts[0] not in {"src", "tests", "scripts"}
):
    raise SystemExit(0)

print(target)
PY
)

if [[ -z "$TARGET_FILE" ]]; then
  exit 0
fi

cd "$REPO_ROOT"

uv run ruff check --fix "$TARGET_FILE" 2>&1 || true
uv run ruff format "$TARGET_FILE" 2>&1 || true

exit 0
