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

## Release provenance recovery after artifact expiry

This runbook is scoped to the artifact-backed Release Finalize implementation proposed in [PR #1061](https://github.com/tuanductran/soulmap-ai/pull/1061). It becomes operative only after that implementation is merged into `main`. The current `main` workflow has a different recovery path: it validates the supplied merged release-preparation SHA and rebuilds/verifies release artifacts in the Finalize run; it does not retrieve a 90-day provenance artifact from the original Prep run. Until PR #1061 is merged, operators must follow the workflow revision actually present on `main` and must not apply the artifact-expiry procedure below.

The automated Release Finalize workflow accepts only the immutable provenance
artifact created by the original Release Prep workflow run and attempt. GitHub
Actions artifact retention is finite (currently configured as 90 days for the
Release Prep provenance artifact). When that artifact is expired or unavailable,
the automated workflow must fail closed. Do not substitute a later Release Prep
run, reconstruct a manifest from a mutable pull-request comment, or weaken the
provenance verifier.

If a release tag was created but GitHub Release publication failed after the
original provenance artifact expired, treat recovery as a release-operations
exception requiring a separately reviewed, human-controlled procedure:

1. Open an incident/operations issue referencing the original merged release PR,
   merge commit SHA, release tag, original Release Prep run ID and attempt, and
   the failed Release Finalize run. Do not place tokens, secret values, or private
   user data in the issue.
2. Preserve the original tag and inspect it read-only. Confirm that it is the
   expected immutable annotated tag and resolves to the exact original release
   commit. Never move, force-update, or recreate the tag to make recovery pass.
3. Gather independent GitHub records for the original workflow run and attempt,
   workflow path/ref/SHA, repository, successful conclusion, release-prep branch,
   PR head SHA, merge SHA, and the exact nine-file generated release diff.
   A PR comment is an index only and is not provenance evidence.
4. Have a maintainer who did not author the recovery change independently review
   the evidence and proposed publication operation. Record the reviewer, evidence
   links, exact tag/commit, artifact hashes, and decision in the issue.
5. Do not publish from this runbook alone. The repository does not provide
   an approved standalone command that can restore an expired immutable Prep
   artifact or re-establish the original verifier's complete trust decision.
   Do not substitute a fresh build, invoke the release action manually, or use
   `gh release create` as an undocumented bypass. If publication is required,
   first propose a separate implementation that independently validates the
   original run/attempt, workflow revision, PR head, merge SHA, exact changed-file
   set, and artifact digests. Require independent maintainer review and its own
   regression/CI evidence before using it.
6. If the original artifact or any required evidence cannot be established,
   or no separately approved recovery implementation exists, stop. Keep the
   original tag intact and leave the GitHub Release unpublished.

This procedure is a manual exception path, not an alternate automated trust
path. It does not authorize direct pushes to `main`, changes to branch rulesets,
relaxation of release immutability, or bypass of repository permissions.
