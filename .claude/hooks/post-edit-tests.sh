#!/usr/bin/env bash
# Post-edit hook intent: run pytest on the edited test file after saving.
# Non-blocking. Fast feedback only for the touched test file.

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
    or relative.parts[0] != "tests"
):
    raise SystemExit(0)

print(target)
PY
)

if [[ -z "$TARGET_FILE" ]]; then
  exit 0
fi

cd "$REPO_ROOT"

run_test_command() {
  local output
  local exit_code

  set +e
  output=$("$@" 2>&1)
  exit_code=$?
  set -e

  printf '%s' "$output"
  return "$exit_code"
}

if OUTPUT=$(run_test_command uv run soulmap test "$TARGET_FILE" --tb=short); then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[hook:post-edit-tests] Tests failed for $TARGET_FILE" >&2
  echo "$OUTPUT" >&2
  echo "Test failures in $TARGET_FILE after edit:"
  echo "$OUTPUT"
else
  echo "[hook:post-edit-tests] All tests passed." >&2
fi

exit 0
