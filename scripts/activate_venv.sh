#!/usr/bin/env bash
# Activate the repository virtual environment in your current shell.
#
# Usage (must be sourced):
#   source scripts/activate_venv.sh
#
# This script deliberately does NOT set `-euo pipefail`, unlike every other
# script here. A sourced script runs in the caller's shell, so those options
# would stay set after it returns: the next command that fails, or the next
# reference to an unset variable, would then kill the interactive shell. The
# checks below return non-zero explicitly instead.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Error: this script must be sourced (so it can activate your shell)." >&2
  echo "Run: source scripts/activate_venv.sh" >&2
  exit 1
fi

_soulmap_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)" || return 1
_soulmap_activate="${_soulmap_root}/.venv/bin/activate"

if [[ ! -f "${_soulmap_activate}" ]]; then
  echo "Error: venv not found at .venv/. Create it with:" >&2
  echo "  bash scripts/bootstrap_venv.sh" >&2
  unset _soulmap_root _soulmap_activate
  return 1
fi

# shellcheck disable=SC1090
source "${_soulmap_activate}"
unset _soulmap_root _soulmap_activate
