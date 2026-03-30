#!/usr/bin/env bash
# Session-start hook intent: inject repo context and branch workflow reminder.
# Stdout is meant to be added to the session context by the Codex hook runner.

set -euo pipefail

INPUT=$(cat || true)
REPO_ROOT=$(printf '%s' "$INPUT" | python3 -c '
import json, sys
raw = sys.stdin.read().strip()
if raw:
    try:
        data = json.loads(raw)
    except Exception:
        data = {}
    cwd = data.get("cwd")
    if isinstance(cwd, str) and cwd:
        print(cwd)
        raise SystemExit(0)
print("")
' 2>/dev/null || true)

REPO_ROOT="${REPO_ROOT:-${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}}"

cd "$REPO_ROOT" 2>/dev/null || exit 0

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
LAST_COMMIT=$(git log -1 --format="%h %s" 2>/dev/null || echo "none")

cat <<EOF
=== SoulMap AI - Repo Context ===
Branch:        $CURRENT_BRANCH
Last commit:   $LAST_COMMIT
Uncommitted:   $UNCOMMITTED file(s) changed

Branch workflow rules (.agents/rules/git-and-release.md):
- Never push directly to main
- One branch per logical change: feat/..., fix/..., ci/..., docs/..., test/..., chore/...
- Run python -m pytest -n auto -q before pushing any src/ runtime change
- Run python -m soulmap_runtime.guards.markdown_contract --root . before pushing skills/ or templates/ changes
- Run python -m soulmap_devtools.cli.lint before pushing or tagging a release after editing CHANGELOG.md, root Markdown, or docs
- Push branch -> open PR -> merge -> delete branch

Pre-push checklist:
  python -m soulmap_devtools.cli.format
  python -m soulmap_devtools.cli.lint
  python -m pytest -n auto -q
  python tests/eval_regression/test_safety_evals.py
=================================
EOF

exit 0
