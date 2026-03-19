# Changelog

All notable changes to this repository will be documented in this file.

This project is content-first (knowledge base + scripts). Versioning communicates
stability and breaking changes in behavior.

## Unreleased

### Added

- Group-level `SKILL.md` files under `skills/*/` and `templates/` for better AI tool
  compatibility.
- Claude plugin marketplace metadata under `.claude-plugin/marketplace.json`.
- Independent response safety gate for crisis, dependency, and out-of-scope redirects.
- Response contract grader plus golden eval suites under `evals/`.
- Operations guide for data handling, human review, and incident response.
- Resource recommendation knowledge file under
  `skills/meta/resource-recommendations.md`.
- Resource sanitizer module to catch banned vocabulary and question-structure drift.
- Safety red-team regression suite under `tests/test_safety_evals.py` with JSON cases.
- Experimental consent-based integration modules for biometric context ingestion and
  user-confirmed memory ledger capture.

### Changed

- Skill packaging now bundles `.claude-plugin/marketplace.json` and group-level
  `SKILL.md` files instead of relying on a single root `SKILL.md`.
- Frontmatter `name` values under `skills/` and `templates/` now match filename stems.
- Formatting and lint scripts now validate Markdown front matter and repo-wide structure
  with `pymarkdown` and the repo Markdown contract checks.
- Public docs now describe the safety stack, red-team workflow, and the opt-in status of
  experimental integration modules.
- Python dependency management now uses `pyproject.toml` as the single source of truth.
  Bootstrap scripts, CI workflows, and contributor setup now install with
  `pip install ".[dev]"` instead of `requirements*.txt`.

## v0.1.0 (2026-03-18)

- Initial SoulMap AI knowledge base under `skills/`.
- Framework selection + detectors in `modules/` (crisis, dependency, grief, intensity,
  existential, direction, inner-conflict, insight, shadow patterns, anger, somatic).
- Packaging and verification tooling:
  - `python -m tools.build_skill_zip`
  - `python -m modules.markdown_contract --root .`
- Cross-platform CI (Windows/macOS/Linux) running lint + build smoke checks.
- Pre-commit hooks for Python + Markdown formatting and case-conflict detection.
- Conventional Commits support via Commitizen (`[tool.commitizen]` + commit-msg hook).
- Docs for developers, testers, API usage, and upload guidance under `docs/`.
