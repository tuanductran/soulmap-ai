#!/usr/bin/env bash
# SessionStart hook: inject repo context and branch workflow reminder.
# Stdout is added to Claude's context at session start.

set -euo pipefail

REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

cd "$REPO_ROOT" 2>/dev/null || exit 0

# Get current branch and status
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
LAST_COMMIT=$(git log -1 --format="%h %s" 2>/dev/null || echo "none")

cat <<EOF
=== SoulMap AI  -  Repo Context ===
Branch:        $CURRENT_BRANCH
Last commit:   $LAST_COMMIT
Uncommitted:   $UNCOMMITTED file(s) changed

Branch workflow rules (.claude/rules/git-and-release.md):
- Never push directly to main
- One branch per logical change: feat/..., fix/..., ci/..., docs/..., test/..., chore/...
- Run python -m pytest -q before pushing any modules/ change
- Run python -m modules.markdown_contract --root . before pushing skills/ or templates/ changes
- Push branch -> open PR -> merge -> delete branch

Pre-push checklist:
  python3 -m tools.format
  python3 -m tools.lint
  python3 -m pytest -q
  python tests/test_safety_evals.py
=================================
EOF

exit 0
