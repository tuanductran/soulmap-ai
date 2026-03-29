#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: '${PYTHON_BIN}' not found. Set PYTHON_BIN or install Python." >&2
  exit 1
fi

cd "${ROOT_DIR}"
"${PYTHON_BIN}" -m tools.bootstrap_venv
