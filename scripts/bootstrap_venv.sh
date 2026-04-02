#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: 'uv' not found. Install uv and rerun bootstrap." >&2
  exit 1
fi

cd "${ROOT_DIR}"
uv run soulmap bootstrap
