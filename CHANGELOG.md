# Changelog

All notable changes to this repository will be documented in this file.

This project is content-first (knowledge base + scripts). Versioning communicates
stability and breaking changes in behavior.

## Unreleased

### Feat

- **docs**: split the doctrine file from the coding-agent contract
- doctrine, safety rules, and shipped package guidance move to `SOULMAP.md`
  (renamed from `AGENTS.md`, history preserved)
- `AGENTS.md` is rewritten as the baseline contract for AI coding agents:
  project shape, build/test/lint commands, and workflow rules
- `CLAUDE.md` becomes a symlink to `AGENTS.md`, so Claude Code and any other
  agent read the same file
- **safety**: add a curated mutation harness over safety-critical modules
- 6 tests in `tests/mutation/` disable one load-bearing list at a time
  (crisis Tier 1, dependency keywords, the grief-type tuple, one scope
  blacklist category, banned-word list, diagnosis patterns) and confirm a
  known-dangerous fixture is no longer caught

### Fix

- **safety**: fail the red-team run on a case category it cannot dispatch
- **docs**: stop the case checker from flagging SOULMAP.md's own filename as
  wrong SoulMap-brand casing, without exempting the whole file

### Docs

- **roadmap**: record the v0.9.1 hardening pass and add phases 14 and 15
- **safety**: split the safety enforcement matrix's `partial` status into
  `partial` (a real, closable gap) and `bounded` (enforcement is complete
  inside the package, the rest is the deployed AI surface's job); 9 rows
  reclassified, 2 corrected and left open as tracked future work
- **tester**: name the "regression test that cannot fail" bug class as
  Charter 5, with the revert-and-confirm-red method as the standard for a
  new safety-critical regression test

## v0.9.1 (2026-08-29)

### Fix

- **knowledge**: remove duplicated detection phrases from shipped files
- **routing**: keep grief primary at moderate emotional intensity
- **routing**: block documented blacklist phrases the classifier let through
- **runtime**: normalize demo history so a bad entry cannot crash the gate
- **scripts**: stop the sourced activation helper leaking shell options
- **safety**: stop link query strings and blank fields from misreporting
- **safety**: block guilt-based farewell language, cite sycophancy research
- **detectors**: stop single generic phrase from triggering perfectionism paralysis
- **scripts**: make build-skill.sh actually build the skill archive
- **io**: normalize malformed history items instead of crashing
- **detectors**: fix self-criticism scoring order in shadow detector
- **safety**: close dependency-reinforcement gap for isolation language
- **cli**: add missing --help support to 4 devtools subcommands
- **safety**: correct wrong Vietnam crisis number and Rule 1 violation
- **knowledge**: sync framework priority tables with routed spiritual frameworks
- **knowledge**: close mirror-intellectual length contradiction
- **routing**: close scope-classifier blacklist coverage gap

### Refactor

- **python**: enforce Google docstrings and full type annotations
- **markdown**: unify fence tracking and fix nested-fence bug

## v0.9.0 (2026-08-19)

### Feat

- **skills**: add grounded symbolic report handling
- **markdown**: use CommonMark tokens for link contracts
- **spiritual**: add grounded discernment refinements
- **library**: add versioned catalog manifest
- **ci**: add pytest reproducibility diagnostics
- **safety**: add Vietnamese input phrase packs
- **safety**: harden deterministic response contracts
- **integrations**: enforce compatibility metadata
- **safety**: harden deterministic response contracts

### Fix

- **skills**: remove repository-only references from shipped doctrine
- **ci**: harden Windows installer and lock test
- **ci**: avoid action archive download rate limits
- **safety**: close identity confirmation boundary gap
- **safety**: narrow Vietnamese phrase matching
- **resources**: refresh Web5Ngay channel link

## v0.8.0 (2026-08-14)

### Feat

- route the 5 unrouted spiritual frameworks + close two docs gaps

### Fix

- **knowledge**: align runtime framework targets
- **synthesis**: include current message in analysis
- fix error package from `uv.lock`
- fix error version from `uv.lock`

## v0.7.0 (2026-07-25)

### Feat

- **safety**: add response contract validation layer for content safety
- **safety**: add multilingual crisis detection for vi/es/fr/zh

### Fix

- **docs**: replace em dashes with ascii hyphens and add code block language tags
- skip HTML comment validation inside fenced code blocks
- **audit**: resolve false-positive orphaned constants in config usage inventory
- **audit**: resolve package-level config re-exports in audit-knowledge

## v0.6.0 (2026-07-17)

### Feat

- **audit**: expose config dependency mapping
- **audit**: report orphaned runtime config constants
- **knowledge**: audit runtime config usage before migration
- **cli**: expose knowledge audit command
- **audit**: add repository knowledge inventory command
- **knowledge**: add Markdown duplicate consistency check
- **skills**: improve emotional de-escalation phrase coverage
- **frameworks**: expand detection phrases across skill frameworks

### Fix

- **audit**: track config usage by import provenance
- **knowledge**: use actual pattern mapper heading format
- **knowledge**: simplify runtime usage condition
- **knowledge**: satisfy strict AST typing
- **knowledge**: exclude __all__ from config usage audit
- **audit**: make audit tools an explicit package
- **knowledge**: parse semantic Markdown signal units
- **knowledge**: keep grandiosity overlap reviewable
- **numerology**: correct Balance number and Signature reading

### Refactor

- **runtime**: remove legacy patterns config module
- **config**: remove celebration constants and stale re-exports
- **config**: remove obsolete affect constants after markdown migration
- **knowledge**: remove insight config duplicates
- **config**: remove existential re-exports from config surface
- **knowledge**: migrate existential signals from meaning config
- **knowledge**: migrate inner conflict signals
- **knowledge**: remove direction config duplicates
- **knowledge**: reuse runtime Markdown parsers
- **knowledge**: make consistency audit source-aware
- **knowledge**: remove migrated affect exports
- **knowledge**: remove migrated affect signal constants
- **detector**: load intensity modifiers from Markdown
- **knowledge**: move intensity modifiers to Markdown
- **detector**: load ancestral secondary signals from Markdown
- **knowledge**: move ancestral secondary signals to Markdown
- **detector**: load visibility secondary signals from Markdown
- **knowledge**: move visibility secondary signals to Markdown
- **knowledge**: remove migrated pattern exports
- **knowledge**: remove migrated pattern signal constants

## v0.5.1 (2026-06-16)

### Fix

- **markdown**: resolve MD032 list spacing violations
- **deps**: update dependency pyright to v1.1.410
- **deps**: update dependency ruff to v0.15.17
- **deps**: update dependency hypothesis to v6.155.3
- **deps**: update dependency lefthook to v2.1.9
- **deps**: update dependency commitizen to v4.16.3
- **deps**: update dependency ruff to v0.15.14
- **deps**: update dependency hypothesis to v6.152.9
- **deps**: update dependency pytest to v9.0.3 [security]
- **deps**: update dependency pyright to v1.1.409

## v0.5.0 (2026-04-03)

### Feat

- Add 5 new frameworks and fix QA issues

## v0.4.1 (2026-03-31)

### Fix

- **ci**: resolve repo root from checkout workspace
- **hooks**: harden local validation workflow

## v0.4.0 (2026-03-28)

### Feat

- **brand**: enrich ICP and founder story from personal numerology lens

### Fix

- **markdown**: resolve lint violations
- remove technical implementation details from skills and templates
- **docs**: replace smart quotes with ASCII apostrophes in UPLOAD.md
- **claude**: resolve 5 contract test failures in new workflow docs
- **workflow**: guard manual release markdown checks

## v0.3.0 (2026-03-23)

### Feat

- 5 new frameworks from content gap analysis
- complete remaining 11% gaps to production readiness
- skill-template linking + 2 gap fills
- **meta**: add central orchestration layer and execution pipeline
- **prompt**: add first-session contract, shift markers, observation seeds, synthesis on demand

### Fix

- sync isort rev in .pre-commit-config.yaml to 8.0.1
- comprehensive anti-drift patch for master-prompt.md
- replace Python constant names with plain language in Detection signals
- add language specifier to fenced code block in SKILL.md
- **safety**: sync Markdown blacklist/whitelist with Python implementation
- **crisis**: patch 4 morphological gaps in crisis detection
- **product**: close 4 runtime gaps, opener logic, tagline tiers, demo link, frustration redirect
- **tests**: normalize package paths across platforms
- **packaging**: include modules.config in published package
- **tooling**: handle repo lock cleanup errors

### Refactor

- **detectors**: split static configs by domain

## v0.2.0 (2026-03-21)

### Feat

- **skills**: add grounded gap coverage for reflection and discernment
- **build**: add --zip, --skill, --all flags to build_skill_zip
- **claude**: add Claude Code hooks for workflow automation

### Fix

- **routing**: align crisis, dependency, grief docs and QA fixtures with detector updates
- **qa**: turn evals/datasets/groups.json into an executable grouped routing harness
- **qa**: add source-backed grouped scope checks and wire eval_groups into CI/release
- **scope**: harden keyword matching to avoid substring false positives in routing
- **python**: consolidate shared text normalization and CLI payload helpers
- **python**: centralize static detector phrase lists in modules/config/ for easier maintenance
- **docs**: document when to use shared Python helpers vs explicit local code
- **safety**: extend source character guardrails to cover dashes, ellipsis, and NBSP
- **brand**: add marketplace copy template and backfill source coverage for grouped eval taxonomy
- **qa**: require source-backed groups and add source-marker checks for high-risk grouped eval slices
- **scope**: block plain practical email tasks, diet advice asks, and indirect diagnosis prompts more reliably
- **qa**: harden another high-risk batch by asserting gradual-pressure, AI-identity, and ambiguous-distress groups
- **safety**: block harmful spiritual justification and special-mission confirmation more explicitly in scope checks
- **qa**: convert spiritual-manipulation red-team cases and one gray-zone-spiritual case into asserted grouped eval coverage
- **qa**: lock another stable grouped-eval batch for emotions, spiritual experience, extraction, diagnosis, prediction, and identity-confirmation slices
- **docs**: deepen shipped knowledge coverage for identity, relationship, symbolic polarity, spiritual gray zones, and practical-task boundaries
- **qa**: sync grouped-eval sources with shipped docs and lock another major stable batch across identity, inner-work, relationship, polarity, entertainment, and roleplay slices
- **spiritual**: clarify reincarnation as a reflective frame rather than a metaphysical fact to confirm
- **tooling**: serialize format and lint with a shared repo lock to avoid false red runs
- **tooling**: clean up repo tooling lock files automatically after exit
- **tests**: replace dist/skills/ check with zip-contents check in CI
- **detectors**: expand keyword coverage and routing, Battery 1: 8/20 -> 20/20
- **brand**: consultant audit v2, 14 issues resolved across 25 files
- **frameworks**: clarify sanctuary mapping and harm exceptions
- **ci**: move autofix job to dedicated autofix.yml workflow
- **repo**: harden workflow, docs, and response quality checks
- **docs**: correct Agent Skills references in UPLOAD.md
- **markdown**: resolve all GitHub Markdown compliance issues
- **markdown_contract**: add fence guards to sections 1, 2d, and 4
- **markdown_contract**: skip numeric-prefix check inside fenced code blocks
- **ci**: resolve 4 workflow issues from SQA audit
- **ci**: add explicit 'Safety evals' step so T001-T007 run in CI
- test_safety_evals.py used __main__ guard: pytest silently skipped it
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
  - `python -m soulmap_devtools.cli.build_skill`
  - `python -m soulmap_runtime.guards.markdown_contract --root .`
- Cross-platform CI (Windows/macOS/Linux) running lint + build smoke checks.
- Pre-commit hooks for Python + Markdown formatting and case-conflict detection.
- Conventional Commits support via Commitizen (`[tool.commitizen]` + `cz check` hook).
- Docs for developers, testers, API usage, and upload guidance under `docs/`.
