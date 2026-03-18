#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_TARGETS=(
  "${ROOT_DIR}/modules"
  "${ROOT_DIR}/tests"
  "${ROOT_DIR}/scripts"
  "${ROOT_DIR}/tools"
)

if [[ -f "${ROOT_DIR}/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

python -m compileall -q "${PYTHON_TARGETS[@]}"

python -m ruff check "${ROOT_DIR}"
python -m ruff format --check "${ROOT_DIR}"
python -m isort --check-only "${ROOT_DIR}/modules" "${ROOT_DIR}/tests" "${ROOT_DIR}/tools"

if python -m pyright --version >/dev/null 2>&1; then
  python -m pyright
fi

# GitHub-flavored Markdown contract checks (links/anchors/fences/headings).
python -m modules.markdown_contract --root "${ROOT_DIR}"

MD_FILES=()
while IFS= read -r -d '' file; do
  MD_FILES+=("${file}")
done < <(
  find "${ROOT_DIR}" \
    \( -path "${ROOT_DIR}/.venv" -o -path "${ROOT_DIR}/.venv/*" \) -prune -o \
    \( -path "${ROOT_DIR}/.ruff_cache" -o -path "${ROOT_DIR}/.ruff_cache/*" \) -prune -o \
    \( -path "${ROOT_DIR}/.pytest_cache" -o -path "${ROOT_DIR}/.pytest_cache/*" \) -prune -o \
    \( -path "${ROOT_DIR}/dist" -o -path "${ROOT_DIR}/dist/*" \) -prune -o \
    \( -path "${ROOT_DIR}/node_modules" -o -path "${ROOT_DIR}/node_modules/*" \) -prune -o \
    -type f -name "*.md" \
    ! -path "${ROOT_DIR}/skills/AGENTS.md" \
    -print0
)

if ((${#MD_FILES[@]})); then
  python -m mdformat --check "${MD_FILES[@]}"
fi

python -m pytest -q
