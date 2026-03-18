#!/usr/bin/env bash
# Usage (must be sourced):
#   source scripts/activate_venv.sh
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_ACTIVATE="${ROOT_DIR}/.venv/bin/activate"

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Error: this script must be sourced (so it can activate your shell)." >&2
  echo "Run: source scripts/activate_venv.sh" >&2
  exit 1
fi

if [[ ! -f "${VENV_ACTIVATE}" ]]; then
  echo "Error: venv not found at .venv/. Create it with:" >&2
  echo "  bash scripts/bootstrap_venv.sh" >&2
  return 1
fi

# shellcheck disable=SC1090
source "${VENV_ACTIVATE}"

