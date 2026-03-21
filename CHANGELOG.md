# Changelog

All notable changes to this repository will be documented in this file.

This project is content-first (knowledge base + scripts). Versioning communicates
stability and breaking changes in behavior.

## v0.2.0 (2026-03-21)

### Feat

- **skills**: add grounded gap coverage for reflection and discernment
- **build**: add --zip, --skill, --all flags to build_skill_zip
- **claude**: add Claude Code hooks for workflow automation

### Fix

- **tests**: replace dist/skills/ check with zip-contents check in CI
- **detectors**: expand keyword coverage and routing -- Battery 1: 8/20 -> 20/20
- **brand**: consultant audit v2 -- 14 issues resolved across 25 files
- **frameworks**: clarify sanctuary mapping and harm exceptions
- **ci**: move autofix job to dedicated autofix.yml workflow
- **repo**: harden workflow, docs, and response quality checks
- **docs**: correct Agent Skills references in UPLOAD.md
- **markdown**: resolve all GitHub Markdown compliance issues
- **markdown_contract**: add fence guards to sections 1, 2d, and 4
- **markdown_contract**: skip numeric-prefix check inside fenced code blocks
- **ci**: resolve 4 workflow issues from SQA audit
- **ci**: add explicit 'Safety evals' step so T001-T007 run in CI
- test_safety_evals.py used __main__ guard; pytest silently skipped it
- all 7 red-team cases now validated on every push/PR
- **deps**: add mdformat==0.7.21 to dev deps
- release.yml calls 'python -m mdformat CHANGELOG.md'
- missing dep caused every release job to fail at changelog step
- **codeql**: bump checkout@v4->v6, setup-python@v5->v6
- aligns with versions used in ci.yml and release.yml
- **codeql**: add concurrency block to prevent duplicate runs
- was the only workflow without concurrency guard
- **qa**: resolve 4 issues from QA audit
- **voice**: correct crisis response word/sentence count to match AGENTS.md Rule 1
  fix(safety): embed crisis hotlines in boundaries-safety, ethics-safety, redirect-templates
  fix(templates): add CRISIS and DEPENDENCY rows to Framework Selector Master table
  docs(changelog): document all changes from recent sessions
- **.claude**: clarify local vs shipped skill boundaries
- **crisis**: embed region hotlines in response_guidance

## v0.1.0 (2026-03-18)

- Initial SoulMap AI knowledge base under `skills/`.
- Framework selection + detectors in `modules/` (crisis, dependency, grief, intensity,
  existential, direction, inner-conflict, insight, shadow patterns, anger, somatic).
- Packaging and verification tooling:
  - `python -m tools.build_skill`
  - `python -m modules.markdown_contract --root .`
- Cross-platform CI (Windows/macOS/Linux) running lint + build smoke checks.
- Pre-commit hooks for Python + Markdown formatting and case-conflict detection.
- Conventional Commits support via Commitizen (`[tool.commitizen]` + commit-msg hook).
- Docs for developers, testers, API usage, and upload guidance under `docs/`.
