# Memory contract

This document defines the bounded continuity contract for the experimental runtime memory layer. It is separate from SoulMap doctrine, safety enforcement, and shipped response knowledge.

## Persistence boundary

Only explicitly user-confirmed continuity items may enter the bounded ledger. The runtime currently permits these categories:

- `insight`
- `preference`
- `recurring_theme`

Every persisted item must also satisfy:

- `user_confirmed=true`
- `sensitive=false` explicitly
- `identifying=false`
- a positive retention period

An absent or uncertain sensitivity classification is rejected. The runtime does not treat missing metadata as consent.

The default retention window is 30 days. Persistence beyond the in-process ledger is the responsibility of the host platform and must preserve the same contract.

## Prohibited persistence

The ledger must not silently persist:

- crisis or emergency disclosures;
- sensitive personal information;
- unnecessary identifying information;
- arbitrary session transcripts;
- inferred personality, diagnosis, attachment style, stage, or other psychological state;
- inferred spiritual status or beliefs;
- content retained solely to increase return frequency or relationship dependence.

Current-session safety signals remain authoritative. Memory cannot lower or bypass safety precedence.

## Lifecycle

| State | Contract |
| --- | --- |
| Empty | Read returns no items. |
| Add | Requires explicit confirmation and all boundary flags. |
| Active | Only non-expired items may be surfaced. |
| Stale | Expired items are never returned and may be pruned. |
| Reset | All continuity state is deleted from the bounded ledger. |
| Opt-out | A refusal returns `FORGOTTEN` and creates no entry. |
| Malformed | Invalid kind, timestamps, retention, or boundary metadata is rejected. |

## Selector boundary

The selector may consume only validated, non-expired continuity items. Memory is context, not authority. The selector must not infer current emotional state, crisis state, identity, or stage from memory alone.

## Synthesis boundary

Synthesis may reference continuity only when the current user message makes it relevant. Longitudinal connections are observations for the user to confirm or reject, not conclusions inherited from memory.

## Reset and deletion

`MemoryLedger.reset()` removes all entries from the in-process ledger. Host integrations must map account/session deletion and opt-out operations to equivalent deletion semantics rather than merely hiding entries from retrieval.

## Failure posture

When memory is empty, stale, malformed, unclassified, sensitive, identifying, or otherwise unavailable, the safe behavior is to continue without it. Memory failure must never become a reason to fabricate continuity.

## Test contract

`tests/test_memory_ledger.py` covers:

- empty memory;
- explicit confirmation;
- missing/true sensitivity classification;
- identifying-content rejection;
- stale memory;
- reset;
- malformed entries;
- opt-out;
- non-persistence by default.
