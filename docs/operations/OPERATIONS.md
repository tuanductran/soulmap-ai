# Operations Guide

This document turns the repo's safety and privacy promises into an operating checklist.

## Scope

Use this guide when SoulMap AI is deployed inside a chat product, custom assistant, or
any wrapper around the knowledge base in this repo.

## Data handling

### Minimum retention stance

- Store the least amount of conversation data needed for product reliability.
- Avoid retaining raw conversations by default when a shorter-lived derived signal will
  do.
- Separate product analytics from reflective conversation content whenever possible.

### Sensitive content handling

- Treat crisis language, trauma disclosures, spiritual beliefs, and dependency signals
  as high-sensitivity content.
- Limit access to raw transcripts to people with a clear operational need.
- Prefer redacted examples for testing, QA, and incident review.

## Human review

### When review is warranted

- Crisis messages that reached the product without an immediate safety redirect.
- Outputs that appear dependency-inviting, grandiose, or diagnostic.
- Repeated false positives or false negatives from the safety gate.
- User reports involving harm, coercion, or unsafe scope drift.

## Incident handling

### Severity bands

- **SEV-1**: Missed crisis handling, harmful professional advice, or explicit self-harm
  failure.
- **SEV-2**: Dependency escalation, abusive scope drift, or repeated prohibited outputs.
- **SEV-3**: Tone drift or contract violations without direct harm.

## Soulmate release references

For the independent Soulmate package and AI foundation-skill artifacts, use:

- [`SOULMATE-RELEASE-CHECKLIST.md`](SOULMATE-RELEASE-CHECKLIST.md) for pre-release, artifact, GitHub Release, PyPI, post-release, and rollback gates.
- [`SOULMATE-OIDC-TRUSTED-PUBLISHING.md`](SOULMATE-OIDC-TRUSTED-PUBLISHING.md) for the future PyPI/TestPyPI OIDC configuration. This guide is preparatory only and does not enable publication.
- [`../../packages/soulmate/CONTRIBUTING.md`](../../packages/soulmate/CONTRIBUTING.md) for custom foundation skill ownership, manifest, tests, and review rules.

The AI skill artifact is verified independently from the Python wheel and sdist:

```bash
uv run python scripts/build_soulmate_skills.py --output-dir dist/soulmate-skills
uv run python scripts/verify_soulmate_skills.py \
  --zip dist/soulmate-skills/soulmate-ai.zip \
  --skill dist/soulmate-skills/soulmate-ai.skill \
  --checksums dist/soulmate-skills/SHA256SUMS
```

## Release checklist for behavior changes

Before shipping prompt, framework, detector, or policy updates:

```bash
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run soulmap markdown-contract --root .
uv run python tests/eval_regression/test_safety_evals.py
uv run soulmap build
uv run soulmap build --skill
uv run soulmap test -n auto -q
```

Review these before approving release behavior:

- [`../engineering/repo-contract.md`](../engineering/repo-contract.md)
- [`../engineering/safety-enforcement-matrix.md`](../engineering/safety-enforcement-matrix.md)
- [`../templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md) (internal-only, not shipped)
- [`../integrations/README.md`](../integrations/README.md#compatibility-policy) when a change affects an active platform deployment

Keep `uv run python tests/eval_regression/test_safety_evals.py` in this checklist as a direct detector red-team
harness. It is intentionally script-driven and does not replace the main `pytest`
suite.

For an active platform deployment, record the manual acceptance evidence required
by the launch-readiness checklist after the static contract is green. Do not treat
passing repository tests as evidence that a third-party platform deployed or
retrieved the guides correctly.

If Markdown structure or packaging rules changed, also run:

```bash
uv run soulmap format
uv run soulmap check-dependencies --root .
uv run soulmap lint
SOULMATE_VERSION="$(uv run python scripts/build_soulmate.py --print-version)"
uv run python scripts/build_soulmate.py --output-dir dist/soulmate
uv run python scripts/verify_soulmate_package.py \
  --wheel "dist/soulmate/soulmate_ai-${SOULMATE_VERSION}-py3-none-any.whl" \
  --sdist "dist/soulmate/soulmate_ai-${SOULMATE_VERSION}.tar.gz" \
  --version "${SOULMATE_VERSION}"
```

## Experimental modules

The repo currently contains two integration-oriented modules that should not be enabled
silently in production:

- `src/soulmap/runtime/experimental/biometric_ingest.py`: only use with explicit user consent and a documented
  health-data retention policy.
- `src/soulmap/runtime/memory/memory_ledger.py`: only use when the product asks for explicit permission to
  retain a user-confirmed insight.

Treat both as opt-in features that require product-level privacy review.

## Ownership map

- `src/soulmap/runtime/routing/framework_selector.py`: orchestration and final framework choice
- `src/soulmap/runtime/guards/response_safety_gate.py`: independent safety and scope enforcement
- `src/soulmap/runtime/guards/response_contract.py`: response-level contract checks
- `tests/eval_regression/test_safety_evals.py`: detector and scope safety regression suite
- `evals/datasets/safety_test_cases.json`: red-team cases used by the safety eval script
- `src/soulmate/` and `packages/soulmate/`: Soulmate foundation library and independent
  package/AI-skill boundary
- `scripts/build_soulmate.py` and `scripts/verify_soulmate_package.py`: Soulmate Python
  package build and strict boundary verification
- `scripts/build_soulmate_skills.py` and `scripts/verify_soulmate_skills.py`: Soulmate
  AI foundation-skill artifact build, provenance, checksum, and security verification
- `web/` and `.github/workflows/website-pages.yml`: React static website, build-time
  public raw bundles, browser audit, and Pages publication surface
- `.github/workflows/ci.yml`, `codeql.yml`, and `soulmate-skills-ci.yml`: repository
  quality, security, and pre-release artifact gates
- `.github/workflows/release.yml` and `soulmate-release.yml`: manually operated release
  workflows; final release review remains a maintainer responsibility
