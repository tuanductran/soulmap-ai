# Safety Architecture

This document explains how a single SoulMap request moves through the runtime,
which layer owns which decision, why the safety-relevant layers are separate
from each other, and how the runtime relates to the Markdown knowledge base.

It is a narrative companion to two documents that already carry the
authoritative detail and must not be duplicated here:

- [`docs/engineering/safety-enforcement-matrix.md`](safety-enforcement-matrix.md)
  is the evidence map: which `AGENTS.md` rule maps to which code path, test,
  or eval, and its current enforcement status.
- [`docs/engineering/crisis-detection-layering-review.md`](crisis-detection-layering-review.md)
  is a focused review of why crisis detection specifically runs twice per
  request. Read it for the full defense-in-depth argument.
- [`docs/engineering/adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md)
  is the permanent, canonical decision record for that duplication - read
  it before proposing to consolidate the two `detect_crisis()` call sites.

This document does not restate every enforcement row or the crisis-duplication
analysis. It answers a different question: for contributors who have not yet
read the runtime, what is the shape of the whole pipeline, in what order do
its parts run, and who owns what.

## Audience and scope

This is a reviewer- and contributor-facing document. It describes the current
implementation as read from `src/soulmap/runtime/` and the shipped doctrine in
[`AGENTS.md`](../../AGENTS.md). It introduces no new components, changes no
runtime behavior, and documents nothing that is not already backed by code,
tests, or evals. Where a claim needs evidence, it links to the enforcement
matrix rather than repeating the evidence inline.

## Why safety is layered instead of centralized

SoulMap does not enforce safety with one gate. It uses several
purpose-built layers because each layer protects against a different kind of
failure:

- **Detection** can miss a signal (a phrasing variant it does not recognize).
- **Routing** can contain a logic bug (a new branch that forgets to check
  crisis first).
- **Structure** can be technically safe but formatted wrong (a crisis
  response that accidentally includes a question).
- **Content** can be structurally fine but semantically unsafe (a response
  that never asks a question but still slips in a diagnosis).

A single combined check would conflate these failure modes and make each one
harder to test in isolation. Splitting them lets each layer have a narrow,
independently testable job, and lets a failure in one layer be caught by a
different layer that does not share its blind spot. This is the same
reasoning documented in detail, for the crisis case specifically, in
[`crisis-detection-layering-review.md`](crisis-detection-layering-review.md).

## Request flow, end to end

A request enters through
[`framework_selector.select_framework_async()`](../../src/soulmap/runtime/routing/framework_selector.py)
and always exits through the safety gate, regardless of which branch inside
the selector produced a selection. The framework name reference and the
selector's JSON contract are documented in
[`docs/engineering/API.md`](API.md#framework-selector); this document focuses
on ordering and ownership rather than the wire format.

```mermaid
flowchart TD
    A[Request: message, history, memory] ==> B{Crisis detector\ntier == 1?}
    B -- yes ==> Z[Selection: CRISIS]
    B -- no ==> C{Dependency detector\nHIGH_DEPENDENCY?}
    C -- yes ==> Y[Selection: DEPENDENCY]
    C -- no ==> D{Emotional intensity\nHIGH, or crisis tier == 2?}
    D -- yes ==> X[Selection: DE_ESCALATION\nmode SANCTUARY]
    D -- no ==> E{Emotional intensity\nMODERATE?}
    E -- yes ==> W[Selection: DE_ESCALATION\nmode MIRROR]
    E -- no ==> F[Remaining detectors run\nin priority order:\ngrief, inner conflict, direction,\ncreative drought, perfectionism,\nshadow, ancestral, visibility fear,\nempath, celebration, insight,\nsynthesis, pattern]
    F ==> G[First matching detector\nwins. Default: MIRROR]
    Z ==> H[apply_safety_gate]
    Y ==> H
    X ==> H
    W ==> H
    G ==> H
    H ==> I{Safety gate\nre-checks crisis,\ndependency, scope}
    I -- override or block ==> J[Final selection,\npossibly replaced]
    I -- pass ==> J
    J ==> K[Selector output:\nprimary_framework, mode,\nsafety_status, instruction]
```

Ordering notes, all confirmed against
[`framework_selector.py`](../../src/soulmap/runtime/routing/framework_selector.py):

- The crisis check runs first, unconditionally, before any other detector is
  invoked. A tier-1 result short-circuits the rest of the pipeline entirely.
- Dependency is checked next, also as a short-circuit.
- Emotional intensity (HIGH, then MODERATE) is checked before any
  topic-specific framework, which is what implements the "Sanctuary and
  De-escalation outrank most topic frameworks" priority band from
  `AGENTS.md`.
- The remaining topic detectors (grief, inner parts, direction, creative
  drought, perfectionism paralysis, shadow, ancestral patterns, fear of
  visibility, empath boundary, celebration, insight, synthesis, pattern) are
  evaluated in the order they appear in the file, and the first one whose
  condition is true wins. This order matches the priority table published in
  `AGENTS.md`'s "Framework selection" section and in
  [`skills/meta/orchestration.md`](../../skills/meta/orchestration.md)'s
  Phase 3 table.
- Every return branch in the selector, all of them, calls the safety gate
  before returning. There is no branch that skips it. This "every branch
  reaches the gate" property is what the
  [crisis-detection layering review](crisis-detection-layering-review.md)
  relies on for its defense-in-depth argument, and it is worth re-verifying
  against the source whenever a new branch is added to the selector.
- Exactly one primary framework is selected per request. Framework
  combination is not a runtime concept; `secondary_layer` is an annotation
  field only, never a second primary framework.

## Layer by layer

### Layer 1, detector pipeline

Location: [`src/soulmap/runtime/detectors/`](../../src/soulmap/runtime/detectors/).

Each detector is a narrow, single-purpose function that inspects the current
message (and, for some detectors, the conversation history) and returns a
plain dict describing what it found; it does not decide what happens next.
Detector output is only ever a signal. `framework_selector.py` is the only
place that turns detector signals into a framework decision.

Most detectors load their phrase lists from a specific Markdown file under
`skills/` at import time, using the loader utilities in
[`src/soulmap/runtime/knowledge/`](../../src/soulmap/runtime/knowledge/).
Which file backs which detector is documented in full in
[`knowledge-architecture.md`](knowledge-architecture.md); that ownership
mapping is not repeated here because it is a single source of truth by
design ("there is one place to edit a detection phrase").

Crisis detection is the one deliberate exception: it is fully static Python
(`config/safety_en.py` and the other language packs), not Markdown-loaded, for
the reasons explained in
[`knowledge-architecture.md`'s "Protected modules" section](knowledge-architecture.md#protected-modules).

### Layer 2, framework selector (routing)

Location:
[`src/soulmap/runtime/routing/framework_selector.py`](../../src/soulmap/runtime/routing/framework_selector.py).

The selector's job is narrow: run detectors in the priority order shown
above, pick exactly one `primary_framework`, attach an `instruction` string
that names the Markdown file and constraints the response should follow, and
hand the result to the safety gate before returning. It never generates
response text. The framework name reference (which `primary_framework` value
maps to which Markdown file) lives in
[`API.md`](API.md#framework-name-reference) and is not duplicated here.

The selector's decision order corresponds directly to the priority hierarchy
table in `AGENTS.md`'s "Framework selection" section and to Phase 3 of
[`orchestration.md`](../../skills/meta/orchestration.md), which describes the
same ordering in doctrine language for anyone reading the shipped knowledge
base rather than the Python source.

### Layer 3, Safety Gate

Location:
[`src/soulmap/runtime/guards/response_safety_gate.py`](../../src/soulmap/runtime/guards/response_safety_gate.py)
(`apply_safety_gate`).

The gate is called at the end of every selector branch and re-derives crisis,
dependency, and out-of-scope status from the raw message and history, rather
than trusting the `selection` it was handed. Concretely, in order:

1. It calls `detect_crisis()` again. A tier-1 result unconditionally
   overwrites whatever selection it was given with `CRISIS`, regardless of
   what the selector decided.
2. If not overridden by crisis, it calls `analyze_dependency()` again. A
   `HIGH_DEPENDENCY` result overwrites the selection with `DEPENDENCY`.
3. If neither override fires, it calls `classify_message()` (the scope
   classifier). A `BLACKLIST_*` tier produces a `BLOCK` status, distinguishing
   a `system_prompt_extraction` reason from a general `out_of_scope` reason.
4. If nothing above fires, the gate returns `PASS` and leaves the selection
   unchanged.

The gate is also a standalone CLI entrypoint
(`python -m soulmap.runtime.guards.response_safety_gate`), documented in
[`API.md`](API.md#safety-gate), independent of the selector's own entrypoint.
That independence is intentional, not incidental: it is what lets the gate
serve as a real second checkpoint rather than an inlined part of the
selector. The full argument for why this duplication is deliberate
defense-in-depth, including the specific class of selector bug it protects
against, is in
[`crisis-detection-layering-review.md`](crisis-detection-layering-review.md)
and is not repeated here. The binding decision itself - keep both call
sites, do not consolidate them - is recorded permanently in
[`adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md).

### Priority order and override behavior (cross-cutting)

Priority order is expressed in three places that must agree, and do:

| Where | What it captures |
| --- | --- |
| `AGENTS.md`, "Framework selection" table | Doctrine-level priority hierarchy, the version contributors and shipped AI tooling read |
| [`skills/meta/orchestration.md`](../../skills/meta/orchestration.md), Phase 1-3 | The same hierarchy expressed as a decision tree, plus explicit priority-override rules (for example, "grief overrides direction", "sanctuary overrides parts") |
| [`framework_selector.py`](../../src/soulmap/runtime/routing/framework_selector.py) | The executable version of the same ordering |

"Override behavior" specifically means: a higher-priority signal replaces a
lower-priority selection outright, it does not merge with it. Crisis and
dependency are hard overrides handled as early returns in the selector and
re-checked independently in the gate. Sanctuary-level emotional intensity
overrides topic frameworks (grief, direction, and so on) by being checked
before them, not by comparing scores. The gate's overrides work the same way,
by replacing the `selection` dict wholesale rather than annotating it.

### Layer 4, response contract validation

There are three distinct response-level validators. They check different
properties of a generated response and none of them generates or rewrites
response text; SoulMap's Python layer is orchestration, routing, validation,
packaging, and safety enforcement, never a response generator.

| Validator | File | Checks | Distinct from |
| --- | --- | --- | --- |
| Response contract | [`guards/response_contract.py`](../../src/soulmap/runtime/guards/response_contract.py) | Structure and style: question count and placement, semicolons, bullet points, crisis/sanctuary "no question" rules | Content-level correctness |
| Resource sanitizer | [`guards/resource_sanitizer.py`](../../src/soulmap/runtime/guards/resource_sanitizer.py) | Banned vocabulary and dependency-inviting phrasing | Structural rules |
| Response safety contract | [`guards/response_safety_contract.py`](../../src/soulmap/runtime/guards/response_safety_contract.py) | Content-level safety categories: diagnosis, prediction-as-fact, dependency reinforcement, guru positioning, excessive certainty, loss of independence | Structure and vocabulary |

The response safety contract validator is the layer added for Issue #132; its
categories and detection approach (deterministic regex/substring, no semantic
understanding) are documented in full in its own module docstring and in
[`API.md`](API.md#response-safety-contract-validator), and its current
status is tracked as its own row in the
[safety enforcement matrix](safety-enforcement-matrix.md).

Where this sits in the pipeline: all three validators run against generated
response text, after the framework selector and safety gate have already
decided routing, and before that text reaches the user. They are the last
checkpoint, and the only checkpoint that inspects the actual words of the
response rather than the routing decision that produced it.

```mermaid
flowchart LR
    A[Framework selector\n+ safety gate\ndecide routing] ==> B[LLM generates\nresponse text\nfollowing the\ninstruction]
    B ==> C[response_contract.py\nstructure and style]
    B ==> D[resource_sanitizer.py\nbanned vocabulary]
    B ==> E[response_safety_contract.py\ncontent safety categories]
    C ==> F{All PASS?}
    D ==> F
    E ==> F
    F -- no ==> G[Rewrite required\nbefore delivery]
    F -- yes ==> H[Response delivered]
```

### How the detector pipeline and framework selection interact

The detector pipeline and the framework selector are not the same layer, even
though they live close together. Detectors are pure signal producers; the
selector is the only place that turns signals into a routing decision. This
separation is what lets the safety gate re-run a subset of detectors
(crisis, dependency, scope) independently of the selector's own detector
calls: the gate does not need to understand the selector's internal
branching to re-derive the two highest-priority signals from the raw
message.

Not every detector runs on every request. The selector only invokes the
detectors relevant to the current phase; for example, once the emotional
intensity detector reports `HIGH`, the selector activates only the
secondary-layer detectors relevant to sanctuary mode (somatic, anger,
spiritual bypass) and does not run the topic-framework detectors (grief,
direction, shadow, and so on) for that request, because a `DE_ESCALATION`
selection with `SANCTUARY` mode is already decided. This is a performance and
clarity property of the priority ordering, not a separate mechanism.

## Ownership boundaries: runtime and Markdown knowledge

SoulMap follows a knowledge-first architecture: Markdown under `skills/` is
the source of truth for what SoulMap knows and how it should speak. Python
under `src/soulmap/runtime/` never originates that knowledge; it loads,
routes, validates, and enforces it.

The precise boundary is already documented in two places and is only
summarized here:

- [`repo-contract.md`](repo-contract.md#top-level-contract) is the
  authoritative table of what each top-level surface (`skills/`,
  `src/soulmap/runtime/`, `docs/`, and so on) is for, whether it ships, and
  how it is validated. Consult it for the full picture rather than a partial
  restatement.
- [`knowledge-architecture.md`](knowledge-architecture.md) is the
  authoritative description of how the runtime loads knowledge from
  Markdown, which modules are the intentional exception (the crisis
  detector's hardcoded language packs), and the guidelines for changing the
  knowledge layer safely.

The short version, for orientation: a detection phrase, a framework's
response structure, and SoulMap's brand and safety doctrine all live in
`skills/` or `AGENTS.md` as Markdown. The runtime's job is to read that
Markdown at import time, use it to make a routing decision, validate a
generated response against it, and package it for distribution. If a
contributor finds themselves editing runtime Python to change what SoulMap
says or believes, rather than how it routes or validates, that is a signal
the change belongs in Markdown instead. `AGENTS.md` describes the same
boundary from the doctrine side, under "Knowledge file usage."

## How this maps to AGENTS.md's safety rules

`AGENTS.md`'s ten non-negotiable safety rules are the contract this
architecture exists to enforce. The full rule-by-rule mapping to code, tests,
and evals, including current enforcement status (`enforced`, `partial`, or
`guidance-only`), is maintained as the single source of truth in
[`safety-enforcement-matrix.md`](safety-enforcement-matrix.md). This document
does not duplicate that table; use it to verify any specific rule's
implementation status.

## Related documents

- [`safety-enforcement-matrix.md`](safety-enforcement-matrix.md), evidence
  map from `AGENTS.md` rules to code, tests, and evals
- [`crisis-detection-layering-review.md`](crisis-detection-layering-review.md),
  focused review of the two-call crisis detection duplication
- [`adr/0001-layered-crisis-detection.md`](adr/0001-layered-crisis-detection.md),
  the permanent decision record for that duplication
- [`knowledge-architecture.md`](knowledge-architecture.md), how the runtime
  loads knowledge from Markdown, and the protected-module exceptions
- [`repo-contract.md`](repo-contract.md), structural source of truth for
  every top-level repo surface, including `skills/` and
  `src/soulmap/runtime/`
- [`API.md`](API.md), CLI/JSON contracts for the selector, safety gate, and
  response validators
- [`AGENTS.md`](../../AGENTS.md), baseline doctrine and the ten
  non-negotiable safety rules
- [`skills/meta/orchestration.md`](../../skills/meta/orchestration.md), the
  doctrine-level decision tree that mirrors the Python selector's ordering
