# Changelog

All notable changes to this repository will be documented in this file.

This project is content-first (knowledge base + scripts). Versioning communicates
stability and breaking changes in behavior.

## Unreleased

- No changes yet.

## 0.1.0 - 2026-03-19

### Added

- Initial SoulMap AI knowledge base under `skills/` and bundled output
  `skills/AGENTS.md`.
- Framework selection + detectors in `modules/` (crisis, dependency, grief, intensity,
  existential, direction, inner-conflict, insight, shadow patterns, anger, somatic).
- Packaging and verification tooling:
  - `python -m modules.package_skills`
  - `python -m tools.build_skill_zip`
  - `python -m modules.markdown_contract --root .`
- Cross-platform CI (Windows/macOS/Linux) running lint + build smoke checks.
- Pre-commit hooks for Python + Markdown formatting and case-conflict detection.
- Conventional Commits support via Commitizen (`[tool.commitizen]` + commit-msg hook).
- Docs for developers, testers, API usage, and upload guidance under `docs/`.
