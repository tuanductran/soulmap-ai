#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

# Use a system interpreter here because `.venv` does not exist yet.
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: '${PYTHON_BIN}' not found. Set PYTHON_BIN or install Python." >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip >/dev/null 2>&1 || true

REQ_DEV="${ROOT_DIR}/requirements-dev.txt"
REQ_RUNTIME="${ROOT_DIR}/requirements.txt"

if [[ -f "${REQ_RUNTIME}" ]]; then
  python -m pip install -r "${REQ_RUNTIME}"
fi

if [[ -f "${REQ_DEV}" ]]; then
  python -m pip install -r "${REQ_DEV}"
fi

echo "OK: venv ready. Activate later with:"
echo "  source .venv/bin/activate"
