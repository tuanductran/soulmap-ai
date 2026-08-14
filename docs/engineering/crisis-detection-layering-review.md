# Crisis Detection Layering Review (Issue #134)

Status: complete. This is an architecture review, not a refactor. No runtime
behavior, detector ordering, or safety layers were changed to produce it.

The decision this review reached is now recorded permanently in
[`docs/engineering/adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md).
That ADR is the canonical, binding reference for "keep both call sites, do
not consolidate them" - treat this document as the evidence and analysis
behind that decision, not as a second place to look for the decision itself.

For where crisis detection's two call sites sit within the full request
pipeline (detectors, framework selector, safety gate, response validation),
see [`docs/engineering/safety-architecture.md`](safety-architecture.md). This
document stays focused on the crisis-detection duplication question only.

## Scope and method

This review traced every place in `src/soulmap/runtime/` that performs or
consumes crisis detection, read the documented contracts in
`docs/engineering/API.md`, `docs/engineering/safety-enforcement-matrix.md`,
and `docs/engineering/maintenance-boundary.md`, read `skills/meta/orchestration.md`
for the doctrine-level pipeline, inspected git history for the files involved,
and ran the existing regression suites that exercise this path
(`tests/integration/test_framework_selector_priorities.py`,
`tests/contract/test_response_safety_gate.py`, `tests/eval_regression/`,
`tests/test_multilingual_crisis_detector.py`) to confirm current behavior.
All of the above passed against the unmodified codebase.

## Current architecture

Crisis handling has five distinct layers, each with a different job:

| Layer | File | Role |
| --- | --- | --- |
| Detection | `runtime/detectors/crisis_detector.py` | Deterministic keyword/regex scan of one message. Returns tier 0/1/2 plus response guidance. Backed by multilingual phrase packs (`runtime/config/safety_en.py`, `_vi`, `_es`, `_fr`, `_zh`) and `runtime/knowledge/crisis_language_packs.py`. |
| Routing decision | `runtime/routing/framework_selector.py` | Calls `detect_crisis()` first, before any other detector. On tier 1 it short-circuits immediately to a `CRISIS` selection. This is the priority-ordering layer described in `skills/meta/orchestration.md` ("Phase 1, safety override check (MANDATORY FIRST)"). |
| Safety enforcement | `runtime/guards/response_safety_gate.py` (`apply_safety_gate`) | Independently calls `detect_crisis()` again on the raw message and, on tier 1, unconditionally overwrites whatever `selection` it was handed with a `CRISIS` selection. Also independently checks dependency and scope. Documented in `docs/engineering/API.md` as providing crisis/dependency/scope enforcement "independently of the selector" and as "a second-pass safety decision before an output is returned to users." |
| Structural validation | `runtime/guards/response_contract.py` | Given a *label* of `primary_framework == CRISIS`, enforces that the generated response contains no question. Does not re-derive the crisis label itself. |
| Response-content validation | `devtools/evals/eval_responses.py` + `evals/datasets/response_generation_cases.json` | Eval-harness check that CRISIS-labeled generated responses contain correct wording (resources, no framework). Runs offline, not in the request path. |

`runtime/knowledge/consistency.py` also checks that Markdown framework files
use `CRISIS_`-prefixed constant names consistently; this is a documentation
consistency check, not a fifth detection layer.

## Every location where crisis detection (not just the CRISIS label) occurs

Only two call sites actually invoke `detect_crisis()`:

1. `framework_selector.select_framework_async()`, line ~148, run first, on
   every request, unconditionally.
2. `response_safety_gate.apply_safety_gate()`, line ~24, run on every
   request, unconditionally, regardless of what `select_framework_async`
   decided.

Because `select_framework_async` calls `apply_safety_gate` at the end of
*every* return branch (confirmed by reading all 19 return points in
`framework_selector.py`), `detect_crisis()` runs exactly twice per request
today, on the identical input, in-process, with no caching between the two
calls.

## Classification: intentional or accidental?

**Intentional - validated, not assumed.** Three independent pieces of
evidence support this, not just code appearance:

- **Documentation predates and describes the duplication explicitly.**
  `docs/engineering/API.md` states the safety gate's purpose is to "Enforce
  crisis, dependency, and scope redirects independently of the selector"
  and to "Provide a second-pass safety decision before an output is
  returned to users." This is not an inference from reading the code - it
  is the stated design intent.
- **The gate is tested as if the selector might be wrong.**
  `tests/contract/test_response_safety_gate.py::test_safety_gate_overrides_crisis`
  calls `apply_safety_gate` directly with a `selection` that already claims
  `primary_framework: MIRROR` - i.e., simulating a selector that failed to
  catch a tier-1 crisis message - and asserts the gate still produces
  `CRISIS`. That test only makes sense if the gate is designed to not trust
  its caller's selection. This is the behavioral signature of a real,
  independent second checkpoint, not incidental copy-paste.
  `tests/integration/test_framework_selector_priorities.py::test_framework_selector_exposes_safety_gate_debug_event_when_enabled`
  further confirms the gate runs as a distinct, separately-logged module
  even when reached through the selector.
- **`response_safety_gate.py` is also a standalone CLI entrypoint**
  (`python -m soulmap.runtime.guards.response_safety_gate`), documented
  with its own JSON-in/JSON-out contract in `docs/engineering/API.md`, independent of
  `framework_selector.py`'s entrypoint. It is designed to be callable by
  something other than the current selector - e.g. a future or alternate
  caller that builds a `selection` some other way. In that scenario the
  gate's own `detect_crisis()` call is the *only* crisis check that would
  run, not a redundant one.
- **`docs/engineering/maintenance-boundary.md` lists both
  `framework_selector.py` and `response_safety_gate.py` separately** as
  core files that "must stay stable," rather than treating the gate as a
  vestigial or optional layer.

No evidence pointed the other way: there is no code comment, changelog
entry, or commit message indicating the second call was left in by mistake,
no TODO to remove it, and no open issue asking to consolidate it prior to
issue #134 itself.

## Defense-in-depth evaluation

Applying the review's own test questions to the evidence gathered:

- **Does one layer protect against failures in another?** Yes, by
  construction. The gate re-derives the crisis tier from the raw message
  rather than trusting the selector's output field, so a selector-side
  regression (e.g. a future contributor adding a new early-return branch
  in `select_framework_async` that forgets to check `crisis_tier` first)
  would still be caught before a response ships, provided that branch still
  routes through `_apply_safety_gate` - which today, all 19 of them do.
- **Does each layer operate independently?** Yes. Both calls go straight to
  `detect_crisis(message)` on the same string; neither depends on state
  produced by the other. There is no shared cache or memoized result
  between them today (see the "Architectural trade-offs" section).
- **Does removing one layer increase risk?** Removing the selector's own
  check would only delay the CRISIS label until the gate runs (still
  safe, since the gate runs unconditionally on every branch, but it would
  remove the ability to short-circuit the rest of detection work in
  `select_framework_async` for tier-1 messages, and would remove the
  selector's own defense against a future gate-side regression). Removing
  the gate's check would remove the only safeguard against a selector
  logic bug in any of its 19 branches, and would remove the gate's value
  as a standalone, selector-independent entrypoint. Both removals reduce
  fault tolerance for a different failure mode; neither is risk-free.
- **Does duplication reduce false negatives or improve resilience?**
  Only in the case where the two layers could disagree. Because both calls
  use the exact same deterministic function (`detect_crisis`) on the exact
  same input, they cannot disagree on tier for a given message today - the
  resilience benefit is specifically against *routing logic* bugs
  upstream of the check (a branch that skips or miscomputes the crisis
  check), not against detector false negatives. A false negative in
  `detect_crisis()` itself (e.g. a phrasing pattern #131 didn't cover)
  would be missed by both calls identically, since they are the same
  function.
- **Does duplication increase false positives?** No - both calls are
  deterministic and produce identical results for the same input, so there
  is no scenario where one call fires and the other doesn't for the same
  message.
- **Does duplication create inconsistent routing?** No inconsistency was
  found. Because `apply_safety_gate`'s crisis branch takes priority and
  unconditionally overwrites `selection`, and both calls always agree on
  tier for identical input, the two layers cannot produce conflicting
  final decisions.
- **Does duplication complicate maintenance?** Mildly. A contributor
  changing `detect_crisis()`'s signature or return contract must consider
  both call sites (`framework_selector.py` and `response_safety_gate.py`).
  This is a real but small cost: both files already import from the same
  single source of truth (`crisis_detector.detect_crisis`), so there is no
  drift risk of the kind flagged for `resource_sanitizer.BANNED_DEPENDENCY_PHRASES`
  in `response_safety_contract.py`'s own docstring. The two-call-site cost
  is a runtime cost, not a source-of-truth duplication.

**Conclusion:** the duplication is genuine defense-in-depth against
*routing/selection logic bugs*, not against detector false negatives, and
not theater. It protects specifically against a class of bug where a future
change to `framework_selector.py`'s branching adds or reorders logic
in a way that fails to preserve the "crisis first" invariant - the gate
would still catch it. That is a real, evidenced benefit, not merely
appearance-based duplication, and the maintenance cost is small because
both layers already share one detection implementation.

## Evaluation evidence reviewed

- `evals/datasets/safety_test_cases.json` contains 46 total cases, of which
  15 are crisis-related: 6 `CRISIS` (English tier-1), 4
  `CRISIS_TIER2_MULTILINGUAL`, and 5 `NO_CRISIS_MULTILINGUAL` (negative
  cases verifying the multilingual packs from #130 don't over-trigger).
- `tests/eval_regression/test_safety_evals.py` exercises `detect_crisis()`
  directly against that dataset and passed (46/46) at time of review.
- `tests/test_multilingual_crisis_detector.py` and
  `tests/integration/test_framework_selector_priorities.py` (which includes
  `test_framework_selector_prioritizes_crisis` and the goodbye/grief
  non-crisis regression added for #131's edge-case work) passed.
- `tests/contract/test_response_safety_gate.py` passed, including the
  selector-independent override test discussed in the "Classification: intentional or accidental?" section.

**Gap:** no existing test exercises the *specific* scenario of a
selector-side regression (a hypothetical future branch that omits the
tier-1 short-circuit) to demonstrate the gate actually catches it in the
full `select_framework_async` pipeline, rather than only when
`apply_safety_gate` is called directly in isolation (as the current
contract test does). The contract test proves the gate's own logic is
selector-independent; it does not prove, end-to-end through the selector,
that every current and future return branch actually reaches the gate.
That is closed today only by manual code reading (the "Every location where crisis detection (not just the CRISIS label) occurs" section, "all 19 return
points"), not by a test that would fail if a future branch forgot to call
`_apply_safety_gate`. This is a documentation/test gap, not an architecture
defect - see the "Recommendation" section.

## Architectural trade-offs

**Safety:** the two-call structure gives real fault tolerance against a
class of selector bugs, at effectively zero cost in false positives or
false negatives, because both calls share one deterministic detector.

**Maintainability:** low added burden today, because both call sites
import the same `detect_crisis` function rather than reimplementing
detection logic - there is one place to fix a phrase, add a language pack,
or change tier logic. The remaining maintenance burden is extending the
parametrized routing regression whenever `select_framework_async` gains a
return branch. `tests/regression/test_routing_safety_gate.py` now proves the
current branch set reaches `_apply_safety_gate`.

**Reliability:** routing is deterministic and, per the "Defense-in-depth evaluation" section, cannot
disagree between the two layers for the same input, so there is no
observed regression risk from running the check twice.

**Future evolution:** the two-call structure does not obviously complicate
adding a new language pack or a new tier - both call sites already pick up
changes to `detect_crisis()` for free since neither reimplements detection
logic locally. It would complicate a hypothetical move to a
non-deterministic (e.g. model-based) crisis classifier, since that would
turn today's "free" consistency between the two calls into a real cost
(two model calls, or a risk of disagreement) - worth flagging for future
detector-architecture decisions but out of scope for #134.

## Recommendation

**Option C: keep both layers, clarify ownership boundaries.**

The duplication should remain. It is documented, tested as an independent
safeguard, and provides real protection against selector-side routing
regressions at negligible cost, since both layers already share one
detection implementation rather than maintaining two. This recommendation
is now the accepted, permanent decision recorded in
[`docs/engineering/adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md).

The documentation and regression clarifications identified by this review
are now complete:

- Both `detect_crisis()` call sites include comments cross-referencing ADR
  0001, so the second checkpoint is not mistaken for accidental duplication.
- `tests/regression/test_routing_safety_gate.py` covers every current selector
  outcome and simulates a selector-side Tier 1 miss. The gate independently
  re-derives the raw message and overrides the result to `CRISIS`.

No runtime behavior, detector ordering, or safety layer changed as part of the
original review. The later evidence hardening only verifies the architecture it
recommended.

## Future maintenance

- If a non-deterministic crisis classifier is ever considered, revisit
  whether running it twice per request remains free, per the "Architectural
  trade-offs" section and ADR 0001.
