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

### Changed

- Skill packaging now bundles `.claude-plugin/marketplace.json` and group-level
  `SKILL.md` files instead of relying on a single root `SKILL.md`.
- Frontmatter `name` values under `skills/` and `templates/` now match filename stems.

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
