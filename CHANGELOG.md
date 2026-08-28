# Changelog

All notable changes to this repository will be documented in this file.

This project is content-first (knowledge base + scripts). Versioning communicates
stability and breaking changes in behavior.

## Unreleased

### Build

- **deps**: refresh the development toolchain to the latest Python 3.11
  compatible releases: ruff 0.16.3 to 0.16.5, hypothesis 6.165.9 to 6.165.10,
  lefthook 2.1.10 to 2.1.11, commitizen 4.17.0 to 4.18.0, plus transitive
  updates. `pip-audit` reports no known vulnerabilities before or after, so
  this is planned maintenance rather than a security response. Supersedes the
  four open Dependabot bump pull requests and reaches a newer ruff than any of
  them

### Fix

- **tooling**: configure pytest-timeout, which had never run. It was installed
  and documented as the hang and deadlock signal, but its own documentation is
  explicit that it "will not time out any tests" until a value is set, and no
  value was set anywhere. Now 60 seconds, against a slowest test of about 2.5
  seconds, so it fires only on a genuine hang
- **tooling**: measure the whole package in coverage. The source was
  `src/soulmap/runtime`, so a bare `pytest --cov` silently measured none of the
  31 devtools modules, even though ROADMAP and the Phase 8 and 12 notes quote
  coverage numbers for them
- **tests**: turn a typo'd pytest marker into a collection error rather than a
  decorator that silently does nothing, and fail an xfail that starts passing
  instead of reporting it green as "xpassed"
- **tests**: surface upstream deprecation warnings as failures. The
  dependency-refresh trigger policy treats a deprecation warning as a reason to
  start a refresh, which only worked if someone noticed it in the output
- **runtime**: replace the two relative imports in the runtime config package
  with absolute ones. The runtime ships and runs standalone, where a relative
  import would break an extracted copy

- **safety**: stop a resource link's query string from counting as a question in
  the response contract. `findahelpline.com/?country=vn` made a valid crisis
  response fail the no-question rule, which would have sent the crisis
  resources back for a rewrite they did not need. Only punctuation inside the
  matched link is excluded, so a real question before or after a link still
  counts
- **governance**: stop a blank P-level metadata field from swallowing the next
  line. The field pattern's leading gap crossed the newline, so a blank
  `Safety boundary` captured the `Evidence` line as its value and the check
  reported `Evidence` as the missing field, pointing the author at the wrong
  line. The pull request was still blocked either way
- **safety**: block guilt/FOMO-based farewell language ("you'll lose
  everything," "the love we shared," "please don't leave me") in generated
  responses, curated from a real Character.AI account-deletion backlash and
  Harvard Business School research on farewell-moment manipulation across
  AI companion products
- **detectors**: fix self-criticism scoring order in the shadow-pattern
  detector so it enriches an already-triggered result instead of being
  silently dropped from the recommendation text or wrongly promoted to a
  standalone shadow trigger
- **io**: normalize malformed conversation-history items in
  `require_list_field` instead of letting every detector crash on a
  missing "content" key
- **scripts**: make `build-skill.sh` actually build the `.skill` archive
  it is named for, instead of the plain zip
- **detectors**: stop a single generic phrase from triggering perfectionism
  paralysis alone, contradicting its own "pattern, not a single instance"
  doctrine; repetition evidence can now come from the current message or
  prior history
- **safety**: correct wrong Vietnam crisis number and Rule 1 violation
- **knowledge**: sync framework priority tables with routed spiritual frameworks
- **knowledge**: close mirror-intellectual length contradiction
- **routing**: close scope-classifier blacklist coverage gap
- **knowledge**: correct stale cross-references and dead defaults found in a
  repo-wide audit
- **cli**: add missing `--help` support to 4 devtools subcommands (bootstrap,
  format, eval-responses, library-manifest)
- **safety**: close dependency-reinforcement gap for isolation-encouraging
  response language ("you don't need them," "better than your friends"), found
  while cross-checking Connecticut SB 5 / Washington Chatbot Disclosure Act
  against existing coverage

### Refactor

- **tooling**: extend the Ruff rule set after auditing it against this
  repository, adding A, DTZ, FURB, ISC, LOG, N, PIE, PT, PTH, RET, and TID with
  relative imports banned outright. Each was already clean or nearly so, so
  these lock in conventions the code already follows. S (flake8-bandit) is
  deliberately excluded: it reports 1300+ hits that are almost entirely
  `assert` inside tests plus the subprocess calls that are the point of the
  developer tooling, CodeQL already runs here, and the dependency-refresh
  policy says not to add a scanner merely because an alternative exists
- **python**: document and fully annotate every Python surface. Ruff now enforces
  `D` (pydocstyle, Google convention) and `ANN` (annotations) across `src/`,
  `tests/`, and `scripts/`, so the convention is a checked contract rather than a
  one-time cleanup. Adds 13 package docstrings, 24 module docstrings, and Google-style
  `Args`/`Returns`/`Raises` sections across the runtime, guards, detectors, and
  developer tooling, and annotates every previously untyped argument. Tightening the
  types surfaced 4 real typing gaps that are fixed here: `repo_tooling_lock` returned
  `Any` instead of `Iterator[None]`, the framework selector compared an `object`-typed
  journey stage against an integer, a celebration test asserted a substring against an
  `object`, and a lock test forwarded untyped arguments into `Path.unlink`
- **markdown**: unify fence tracking across 3 files into one `FenceTracker` and
  fix a nested-fence (four-backtick-wrapping-three-backtick) desync bug; remove
  the orphaned `scripts/soulmap_demo.sh` wrapper

### Test

- **governance**: cover the P-level safety-governance check's event-reading and
  exit-code paths (79% to 100%). This is the CI gate that keeps a pull request
  from changing a safety boundary without naming its ADR, regression evidence,
  and rollback, and it had no coverage of an unusable event, a governance
  failure, or a malformed P-level tag
- **packaging**: cover the Library catalog validation guards (79% to 100%), so
  an unsupported schema version, a foreign library id, or a malformed entry
  cannot silently produce a manifest that misdescribes the artifacts
- **safety**: add the sanctuary and crisis question-rule edge cases the
  safety-enforcement matrix asked for: passing responses in both modes, a
  crisis reply carrying two questions reporting both violations, and the crisis
  rule keying off the primary framework rather than the mode label

### Docs

- **roadmap**: record the package coverage target as met (97%) and name the
  ADR 0003 decision as open tracked work, with what moving it to Accepted
  actually requires
- **safety**: replace the question-rule gap note in the safety-enforcement
  matrix with the edge cases now covered
- **brand**: add a 2026 Stanford sycophancy-study citation to
  `research-backing.md` supporting the mirror principle's refusal to
  validate the user's leaning direction, plus the HBS farewell-manipulation
  and Character.AI deletion-screen findings backing the new banned phrases
- **knowledge**: close doctrine sync gaps found in repo-wide audit
- **tester**: add exploratory charter for real-world spiritual media pressure
- **roadmap**: close completed non-ai maintenance items
- **release**: document dependency-bot authority
- **tester/dev**: document `audit-knowledge`, `eval-markdown-contracts`, and `demo`
  commands
- **adr**: propose a bounded edit-distance crisis-phrase backstop for review
  (ADR 0003, Status: Proposed, no runtime change)
- **regulatory**: add Connecticut SB 5, Washington's Chatbot Disclosure Act, and
  the APA's 2025 health advisory to the companion-AI regulatory landscape
- **knowledge**: complete doctrine wiring for the 5 spiritual frameworks (Dark
  Night of the Soul, Soul Nourishment, Divine Guidance, Sacred Polarity,
  Spiritual Purpose) - add each one's own "Paired template" section, a
  detailed Structure/Opening-constraint/Forbidden-structure/Word-range entry
  in `framework-template-map.md`, and a dedicated question bank section in
  `deep-inquiry-bank.md`; fix `safety-enforcement-matrix.md`'s semicolon/bullet
  row to cite the test file with the actual assertion

### CI

- **governance**: enforce P-level safety metadata
- **maintenance**: add weekly governance review
- **security**: add `pip-audit` dependency vulnerability scanning

### Chore

- **packaging**: define Python tooling distribution boundary
- **tooling**: wire eval validation into the post-edit hook chain

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
