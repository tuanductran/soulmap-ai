---
paths:
  - src/**/*.py
  - tests/**/*.py
  - scripts/**/*.sh
  - pyproject.toml
  - .github/workflows/**/*.yml
  - .github/workflows/**/*.yaml
---

# Performance and scaling rules

Use these rules when a change affects repo speed, CI time, eval cost, packaging time,
or repeated local workflows.

## What performance means here

This repository is not a latency-sensitive web app. The practical bottlenecks are:

- repeated full-tree scans across Markdown and Python files
- subprocess-heavy smoke tests and shell wrappers
- duplicated build, lint, and eval passes
- packaging and extraction work that rereads the same file sets
- CI steps that rerun expensive commands without clear need

Optimize for maintainable workflow speed, not theoretical micro-optimizations.

## Measure before changing

- prefer timing an existing command before rewriting it
- identify whether the cost is file scanning, subprocess startup, packaging, or test scope
- do not add complexity for tiny wins on non-critical paths

## Repo-specific optimization rules

- avoid duplicate repo walks when a shared helper can provide the file list once
- prefer shared helpers in `src/soulmap/devtools/support/` for repo-root discovery,
  file iteration, and command execution
- keep shell wrappers thin so Python remains the single source of behavior
- prefer targeted pytest runs before full-suite runs while iterating
- keep eval datasets focused, each new case should earn its runtime cost
- avoid adding new build steps or wrappers when an existing canonical command already exists

## Python guidance

- prefer clear data structures and direct code over clever abstractions
- reduce repeated normalization, parsing, or file reads when the same helper can be reused
- document non-obvious performance assumptions only when they matter to maintainers
- do not trade away typing, readability, or testability for small speed wins

## CI and workflow guidance

- keep GitHub Actions aligned with the narrowest checks needed for each workflow
- avoid rerunning packaging or eval commands in multiple jobs unless the split is intentional
- prefer caching only when it meaningfully reduces install or test time and does not add drift risk

## Review checklist

- does this change reduce duplicate work rather than move it around
- does it keep one canonical command per workflow
- does it avoid new wrapper layers
- does it keep the repo easier to reason about than before
- are the added checks worth their runtime cost
