# Operations Guide

This document is an operating checklist for people who deploy SoulMap AI inside
a chat product, custom assistant, or wrapper around this repository's knowledge
base. It does not describe a service operated by this repository.

## Scope and deployment boundary

The repository provides Markdown knowledge, local Python tooling, and
distribution artifacts. It does not provide a SoulMap-operated server, account
system, backend, or conversation store. In a standard platform deployment, the
host platform governs conversation processing and retention; see
[the privacy statement](PRIVACY.md).

This guide's data-handling controls apply only when an independent deployment
operator builds or configures a wrapper that actually processes user data.
They do not authorize SoulMap or a host platform to collect data, and they do
not imply that the repository itself receives or stores conversations.

## Data handling

### Default: do not collect or retain conversations

- Do not add conversation logging, analytics, or persistent storage by default.
- Use synthetic evaluation cases from `evals/` for testing and QA.
- Do not treat transient platform context or host-managed history as a
  SoulMap-owned memory store.

### If an external deployment independently processes user data

Before enabling collection or retention, the deployment operator must document
the specific operational purpose, the data fields required, the applicable
notice and consent requirements, the retention period, deletion process,
access controls, and any third-party processors. Collect only what is necessary
for that stated purpose.

- Avoid retaining raw transcripts when a less sensitive, shorter-lived signal
  is sufficient.
- Keep analytics separate from reflective conversation content.
- Define a deletion and incident-response path before storing any transcript.
- Do not imply that these controls are provided by this repository or by
  SoulMap itself; they belong to the operator of the deployed service.

### Sensitive content handling

If an external operator actually processes user data:

- Treat crisis language, trauma disclosures, spiritual beliefs, and dependency
  signals as high-sensitivity content.
- Restrict access to raw transcripts to people with a documented operational
  need.
- Prefer synthetic or redacted examples for testing, QA, and incident review.
- Do not copy sensitive user content into issue trackers, analytics, or
  general-purpose logs.

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
uv run soulmap eval-groups
uv run soulmap eval-responses
uv run soulmap markdown-contract --root .
uv run python tests/eval_regression/test_safety_evals.py
uv run soulmap build
uv run soulmap dev
uv run soulmap test -n auto -q
```

Review these before approving release behavior:

- [`../engineering/repo-contract.md`](../engineering/repo-contract.md)
- [`../engineering/safety-enforcement-matrix.md`](../engineering/safety-enforcement-matrix.md)
- [`../../templates/launch-readiness-checklist.md`](../../templates/launch-readiness-checklist.md) (internal-only, not shipped)
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
uv run soulmap lint
```

## Ownership map

- `src/soulmap/runtime/routing/framework_selector.py`: orchestration and final framework choice
- `src/soulmap/runtime/guards/response_safety_gate.py`: independent safety and scope enforcement
- `src/soulmap/runtime/guards/response_contract.py`: response-level contract checks
- `tests/eval_regression/test_safety_evals.py`: detector and scope safety regression suite
- `evals/datasets/safety_test_cases.json`: red-team cases used by the safety eval script
