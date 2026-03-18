#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/dist"
OUT_ZIP="${OUT_DIR}/soulmap-ai.zip"
DISTIGNORE="${ROOT_DIR}/.distignore"

if [[ -f "${ROOT_DIR}/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

mkdir -p "${OUT_DIR}"

# Keep generated bundle fresh inside the zip and fail if generation fails.
python -m modules.package_skills >/dev/null

rm -f "${OUT_ZIP}"
cd "${ROOT_DIR}"

ZIP_INPUTS=(
  "SKILL.md"
  "CLAUDE.md"
  "README.md"
  "LICENSE"
)

while IFS= read -r -d '' file; do
  ZIP_INPUTS+=("${file#./}")
done < <(find "./skills" "./templates" -type f -print0)

if [[ -f "${DISTIGNORE}" ]]; then
  FILTERED_INPUTS=()
  while IFS= read -r item; do
    skip=0
    while IFS= read -r pattern; do
      if [[ -z "${pattern}" || "${pattern}" =~ ^[[:space:]]*# ]]; then
        continue
      fi
      if [[ "${item}" == ${pattern} ]]; then
        skip=1
        break
      fi
    done < "${DISTIGNORE}"
    if [[ ${skip} -eq 0 ]]; then
      FILTERED_INPUTS+=("${item}")
    fi
  done < <(printf '%s\n' "${ZIP_INPUTS[@]}")
  ZIP_INPUTS=("${FILTERED_INPUTS[@]}")
fi

zip -r "${OUT_ZIP}" "${ZIP_INPUTS[@]}"

echo "OK: ${OUT_ZIP}"
