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

## Release checklist for behavior changes

Before shipping prompt, framework, detector, or policy updates:

```bash
source .venv/bin/activate
python -m tools.eval_conversations
python tests/test_safety_evals.py
python -m tools.build_skill_zip
python -m pytest -q
```

Review these before approving release behavior:

- [`repo-contract.md`](repo-contract.md)
- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
- [`../templates/launch-readiness-checklist.md`](../templates/launch-readiness-checklist.md)

If Markdown structure or packaging rules changed, also run:

```bash
python -m tools.format
python -m tools.lint
```

## Experimental modules

The repo currently contains two integration-oriented modules that should not be enabled
silently in production:

- `modules/biometric_ingest.py`: only use with explicit user consent and a documented
  health-data retention policy.
- `modules/memory_ledger.py`: only use when the product asks for explicit permission to
  retain a user-confirmed insight.

Treat both as opt-in features that require product-level privacy review.

## Ownership map

- `modules/framework_selector.py`: orchestration and final framework choice
- `modules/response_safety_gate.py`: independent safety and scope enforcement
- `modules/response_contract.py`: response-level contract checks
- `tests/test_safety_evals.py`: safety regression suite
- `tests/safety_test_cases.json`: red-team cases used by the safety eval script
