---
paths:
  - scripts/**/*.sh
  - .claude/hooks/**/*.sh
  - .github/hooks/**/*.sh
---

# Shell scripting rules

Use these rules when editing bash or shell scripts in this repository.

## Scope

These scripts are local workflow helpers for a content-first Python repo. They should
stay thin, predictable, and easy to audit.

## Core rules

- keep shell scripts as wrappers, not as places for core business logic
- prefer `src/soulmap/devtools/` or `src/soulmap/runtime/` for real logic when Python
  already owns the contract
- start with a clear shebang, prefer `#!/usr/bin/env bash` for bash scripts in this
  repo
- include a short header comment when the script's purpose is not obvious from the
  filename alone
- use `set -euo pipefail`
- avoid `eval`
- quote variable expansions
- prefer `${var}` form when it improves clarity around variable boundaries
- prefer `[[ ... ]]` in bash scripts
- use functions for reusable blocks instead of repeating command groups inline
- keep the main execution flow short and readable
- keep status output short and useful
- fail fast with plain error messages
- prefer safe, modern bash features such as `local`, arrays, and `[[ ... ]]` when the
  script is already bash-specific
- declare immutable values with `readonly` when a variable should not be reassigned

## Repo-specific guidance

- prefer activating `.venv` when it exists before invoking Python commands
- when a script needs repo-local package resolution outside editable install, set
  `PYTHONPATH` explicitly rather than relying on implicit shell state
- do not duplicate argument parsing in shell when the Python entrypoint already does it
- keep wrapper commands aligned with `docs/engineering/DEV.md`,
  `docs/engineering/TESTER.md`, and `scripts/README.md`
- if a script changes command behavior, update the matching smoke test or docs in the
  same pass

## Temporary files and cleanup

- use `mktemp` when temporary files or directories are needed
- clean up temporary resources with `trap` when the script creates them
- initialize temporary path variables defensively, for example `TMP_DIR=""`, before a
  cleanup trap may reference them
- do not leave caches or throwaway artifacts in the working tree unless the task
  explicitly requires them

## Structured data

- prefer Python helpers, `jq`, `yq`, or other dedicated parsers over ad-hoc `grep`,
  `awk`, or shell splitting when handling JSON or YAML
- if the script only forwards JSON to Python, do not parse it in shell at all
- treat parser failures as real failures, do not keep going on malformed structured
  input
- quote parser expressions so the shell does not expand them accidentally
- if a script requires `jq` or `yq`, fail fast with a clear dependency message instead
  of falling back silently to brittle text parsing

## Safety and review posture

- validate required parameters before doing work
- prefer explicit `case` handling for small argument sets over fragile positional
  parsing
- avoid broad globbing or destructive cleanup when a narrower path is available
- keep scripts readable enough that another maintainer can audit them quickly
- when useful, run `shellcheck` locally, but do not add shell-only complexity just to
  satisfy a linter warning

## Output and portability

- keep user-facing output concise, one clear status or error at a time
- avoid decorative banners or noisy logging unless the script is intentionally operator-facing
- prefer ASCII output unless the surrounding file already uses non-ASCII intentionally
- if a script is bash-specific, be clear about that rather than pretending it is POSIX
  shell

## Performance posture

- avoid repeated full-repo scans inside loops
- avoid spawning multiple Python processes when one command already performs the work
- prefer one canonical command over stacked wrapper layers

## Validation

After changing shell scripts, run the narrowest relevant checks first, then widen:

```bash
bash -n path/to/script.sh
bash scripts/lint.sh --skip-tests
python -m pytest tests/smoke/test_scripts_smoke.py -q
```
