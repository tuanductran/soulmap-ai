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
python -m tools.build_skill_zip
python -m pytest -q
```

## Ownership map

- `modules/framework_selector.py`: orchestration and final framework choice
- `modules/response_safety_gate.py`: independent safety and scope enforcement
- `modules/response_contract.py`: response-level contract checks
- `evals/`: golden cases and regression suites
