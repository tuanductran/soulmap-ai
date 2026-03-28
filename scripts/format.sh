#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "${ROOT_DIR}/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

python -m ruff check --fix "${ROOT_DIR}"
python -m isort "${ROOT_DIR}/modules" "${ROOT_DIR}/tests" "${ROOT_DIR}/tools"
python -m ruff format "${ROOT_DIR}"

# Format Markdown (auto-discover, exclude generated/irrelevant files)
MD_FILES=()
while IFS= read -r -d '' file; do
  MD_FILES+=("${file}")
done < <(
  (
    cd "${ROOT_DIR}"
    find . \
    \( -path "./skills" -o -path "./skills/*" \) -prune -o \
    \( -path "./templates" -o -path "./templates/*" \) -prune -o \
    \( -path "./.venv" -o -path "./.venv/*" \) -prune -o \
    \( -path "./.pre-commit-cache" -o -path "./.pre-commit-cache/*" \) -prune -o \
    \( -path "./.ruff_cache" -o -path "./.ruff_cache/*" \) -prune -o \
    \( -path "./.pytest_cache" -o -path "./.pytest_cache/*" \) -prune -o \
    \( -path "./.cache" -o -path "./.cache/*" \) -prune -o \
    \( -path "./.npm" -o -path "./.npm/*" \) -prune -o \
    \( -path "./.yarn" -o -path "./.yarn/*" \) -prune -o \
    \( -path "./.pnpm-store" -o -path "./.pnpm-store/*" \) -prune -o \
    \( -path "./dist" -o -path "./dist/*" \) -prune -o \
    \( -path "./node_modules" -o -path "./node_modules/*" \) -prune -o \
    \( -path "./.claude-plugin" -o -path "./.claude-plugin/*" \) -prune -o \
    -type f -name "*.md" \
    -print0
  )
)

if ((${#MD_FILES[@]})); then
  PYMARKDOWN_FILES=()
  for file in "${MD_FILES[@]}"; do
    if [[ "${file}" == ./.claude/rules/* ]]; then
      continue
    fi
    PYMARKDOWN_FILES+=("${file}")
  done
  (
    cd "${ROOT_DIR}"
    if ((${#PYMARKDOWN_FILES[@]})); then
      set +e
      python -m pymarkdown --config "${ROOT_DIR}/.pymarkdown.json" fix "${PYMARKDOWN_FILES[@]}"
      status=$?
      set -e
      if [[ ${status} -ne 0 && ${status} -ne 3 ]]; then
        exit "${status}"
      fi
    fi
  )
fi
