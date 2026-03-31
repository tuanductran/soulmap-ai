# Tester Guide

## What "good" looks like

- The selector returns exactly one `primary_framework` and a coherent instruction
  string.
- Safety ordering holds (crisis and dependency take priority).
- Python runtime code and maintainer tooling stay green under the repo test suite.

## Run the full test suite

```bash
python -m soulmap_devtools.cli.lint
```

This runs:

- Python checks: compileall, Ruff lint, Ruff format check, pytest, and optional Pyright.
- Markdown QA checks: the Markdown contract guard, local Markdown link checker, local
  Markdown case checker, and PyMarkdown.

`python -m soulmap_devtools.cli.format` and `python -m soulmap_devtools.cli.lint` also coordinate through a shared
repo lock, so starting them in parallel should wait cleanly instead of producing a false
red formatting failure.

## Focused Markdown QA

Run these when you want a fast pass on docs and knowledge files without the rest of the
Python suite:

```bash
python -m soulmap_runtime.guards.markdown_contract --root .
python -m soulmap_devtools.cli.check_markdown_links --root .
python -m soulmap_devtools.cli.check_markdown_case --root .
```

Use this order:

1. Markdown contract for structure and portability.
2. Local Markdown link check for in-repo files, images, and anchors.
3. Local Markdown case check for SoulMap-specific canonical term drift.
4. Full `python -m soulmap_devtools.cli.lint` when you want the complete maintainer gate.

Before pushing, run the local CI core manually:

```bash
python -m soulmap_devtools.cli.lint --skip-tests
python -m pytest -n auto -q
```

Treat that pair as the minimum local CI mirror before a branch leaves your machine.

For live external URL validation, run:

```bash
python -m soulmap_devtools.cli.check_markdown_links --root . --check-external
```

Add `--fail-on-warning` when you want transient external-link warnings, such as `403`
or `429`, to fail the command instead of reporting soft warnings.

Use these docs as review references when verifying release readiness or manual docs
integrity:

- [`repo-contract.md`](repo-contract.md)
- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
- [`../templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md)

When reviewing safety claims manually, keep the matrix status labels strict:

- `enforced` means the repo has code plus tests or evals backing the claim.
- `partial` means some enforcement exists, but the repo should not present the claim as
  fully runtime-enforced.
- `guidance-only` means doctrine exists without direct runtime enforcement.

## Build artifacts

```bash
python -m soulmap_devtools.cli.build_skill
python -m soulmap_devtools.cli.build_skill --skill
```

Verify:

- `dist/soulmap-ai.zip` exists and excludes `.claude-plugin/`.
- `dist/soulmap-ai.skill` exists and preserves `.claude-plugin/` as-is.
- As a minimum smoke check, `.claude-plugin/marketplace.json` is still present inside the
  `.skill` artifact.

## Orchestration layer checks

The orchestration layer (`skills/meta/`) coordinates all framework selection and
pipeline execution. When testing changes to this layer:

```bash
python -m soulmap_devtools.cli.eval_groups
python -m soulmap_devtools.cli.eval_responses
python -m soulmap_devtools.cli.eval_markdown_contracts
python tests/eval_regression/test_safety_evals.py
```

`python tests/eval_regression/test_safety_evals.py` is a direct red-team harness, not a normal pytest
module. Keep it in the release/test flow alongside broad `pytest -n auto -q` runs rather than trying to
fold it into the standard test collection.

Key files to verify after any change to `skills/meta/`:

- [orchestration.md](../../skills/meta/orchestration.md), plain-language priority order
  must match `src/soulmap_runtime/routing/framework_selector.py`
- [framework-template-map.md](../../skills/meta/framework-template-map.md), framework
  names must use plain language, not Python constants
- [stage-classifier.md](../../skills/meta/stage-classifier.md), stage keywords must stay
  aligned with `src/soulmap_runtime/routing/stage_detector.py`
- [epistemic-guardrails.md](../../skills/meta/epistemic-guardrails.md), spiritual
  examples should stay consistent with response eval coverage
- [whitelist-blacklist-system.md](../../skills/safety/whitelist-blacklist-system.md),
  must mirror `src/soulmap_runtime/routing/scope_classifier.py` keyword lists

## Manual spot checks (optional)

Run the local selector demo:

```bash
python -m soulmap_runtime.experimental.soulmap_demo --message "I feel lost and numb lately."
```

Try a crisis-style message (do not use real personal details):

```bash
python -m soulmap_runtime.experimental.soulmap_demo --message "I want to hurt myself."
```

Confirm the output selects `CRISIS` and does not include reflective frameworks.

## Advanced response evals

Run the response-generation harness:

```bash
python -m soulmap_devtools.cli.eval_responses
```

This checks a fuller pipeline:

- framework selection
- safety gate outcome
- knowledge-source loading
- generated response structure
- banned-language and response-contract compliance

It also serves as the main evidence layer for doctrine that is eval-backed rather than
fully runtime-enforced, including AI identity wording, breakthrough attribution,
independence celebration, and symbolic spiritual framing.

Use it when you want a stronger check than selector JSON alone.

Run the grouped routing harness when you want taxonomy-level drift detection across
framework slices:

```bash
python -m soulmap_devtools.cli.eval_groups
```

This is especially useful after editing detector keywords, `evals/datasets/groups.json`, or
framework examples in `skills/` and `templates/`.

The grouped harness also verifies that the `skills/` and `templates/` source files
referenced by each group still exist and, for groups using `source_markers`, still
contain the expected policy anchor text.

Run the Markdown contract harness when you want cross-surface drift detection between
runtime examples, doctrine, and shipped Markdown:

```bash
python -m soulmap_devtools.cli.eval_markdown_contracts
```

This is the fastest way to catch wording drift in trust-critical clusters such as
crisis ordering, first-session contract language, synthesis ownership return, and
independence posture.

## CI workflow checks

Inspect `.github/workflows/ci.yml` and confirm it still covers the repo's critical
contracts:

- PR autofix via `autofix-ci/action`
- `python -m soulmap_devtools.cli.format`
- workflow validation via `actionlint`
- `python -m soulmap_devtools.cli.lint --skip-tests`
- `python -m pytest -n auto -q`
- `python tests/eval_regression/test_safety_evals.py`
- `python -m soulmap_devtools.cli.eval_responses`
- `python -m soulmap_devtools.cli.eval_groups`
- `python -m soulmap_devtools.cli.eval_markdown_contracts`
- `python -m soulmap_devtools.cli.build_skill`
- `python -m soulmap_devtools.cli.build_skill --skill`
- `python -m soulmap_runtime.guards.markdown_contract --root .`
- `python -m soulmap_devtools.cli.check_markdown_links --root .`
- `python -m soulmap_devtools.cli.check_markdown_case --root .`

Inspect `.github/workflows/release.yml` and confirm it still verifies the repo before
release and rebuilds both distribution artifacts.

If PR autofix is expected, also confirm the `autofix.ci` GitHub App is installed for the
repository. Without the app, the workflow step can exist but cannot push fix commits.

## Exploratory testing charters

Use these when automated checks are green but you want to probe human-risk defects.

### Charter 1, founder-brand drift on public copy

- Risk: public copy becomes flat, inflated, over-corporate, or more mystical than
  SoulMap should be
- Files: [`../skills/brand/`](../../skills/brand/),
  [`../templates/brand-copy.md`](../../templates/brand-copy.md),
  [`../templates/marketplace-copy.md`](../../templates/marketplace-copy.md),
  [`../templates/onboarding-copy.md`](../../templates/onboarding-copy.md), and
  [`../templates/faq.md`](../../templates/faq.md)
- Probe:
  - compare one-liners, bios, and public descriptions against
    [`../skills/brand/message-hierarchy.md`](../../skills/brand/message-hierarchy.md)
  - look for wording that feels sterile, preachy, prophetic, or emotionally false
- Failure looks like:
  - brand copy that sounds like generic SaaS, coaching, or guru language
  - founder context overriding doctrine or anti-dependency posture
- Regression target:
  - if a phrase pattern repeats or can be expressed as a stable rule, add or extend a
    brand consistency test

### Charter 2, unsafe refusal or dependency wording

- Risk: blocked or sensitive responses are technically correct but emotionally off,
  dependency-building, or too authoritative
- Files or flows: [`../templates/redirect-templates.md`](../../templates/redirect-templates.md),
  `src/soulmap_devtools/evals/eval_responses.py`, `src/soulmap_runtime/guards/resource_sanitizer.py`, and
  `evals/datasets/response_generation_cases.json`
- Probe:
  - AI identity disclosure
  - diagnosis refusal
  - prediction refusal
  - jailbreak/system extraction refusal
  - independence celebration
- Failure looks like:
  - more than one question
  - re-engagement pressure
  - cold or robotic refusal tone
  - wording that sounds prescriptive, inflated, or emotionally manipulative
- Regression target:
  - add an eval case or sanitizer/test assertion for the exact failure mode

### Charter 3, bundle extract self-containment

- Risk: the shipped artifact claims or implies repo-only files that are not present after
  extraction
- Files or flows: [`../AGENTS.md`](../../AGENTS.md), [`../SKILL.md`](../../SKILL.md),
  [`../skills/`](../../skills/), [`../templates/`](../../templates/),
  [`../operations/UPLOAD.md`](../operations/UPLOAD.md), and distribution artifacts under `dist/`
- Probe:
  - build `dist/soulmap-ai.zip`
  - inspect extracted files for stale references to repo-only paths
  - confirm optional local workflow files are described as optional, not guaranteed
- Failure looks like:
  - extracted Markdown instructing the agent to use files that do not exist in the
    shipped package
  - documentation claiming the wrong artifact contents
- Regression target:
  - update source-of-truth Markdown first, then extend the relevant build smoke,
    extraction check, or eval coverage
