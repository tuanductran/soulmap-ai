# ADR 0002: Deterministic Response Safety Enforcement

## Status

Accepted

## Context

SoulMap delegates response wording to the underlying language model. The Python
runtime routes requests and validates generated text before delivery. Issue #132
introduced `response_safety_contract.py` to detect six response-safety categories:
diagnosis, prediction as fact, dependency reinforcement, guru positioning,
excessive certainty, and loss of user independence.

The validator is intentionally deterministic. It performs fixed regex and
substring checks, produces an auditable list of matched patterns, and never
rewrites or generates response text. Its known limitation is that a fixed
pattern set cannot infer every paraphrase or implied violation.

Issue #132 named semantic validation as future work. Without a recorded decision,
that note can be read as permission to add an LLM-based classifier to a safety
path or to CI. Such a change would conflict with the existing architecture:
`SOULMAP.md` defines Python as an enforcement and validation layer, and
[`known-limitations.md`](../known-limitations.md#safety-enforcement-boundaries)
defines safety enforcement and regression evaluation as deterministic.

## Decision

Keep `response_safety_contract.py` and all other response-safety enforcement
deterministic. SoulMap will not add semantic or LLM-based safety classification
to the runtime enforcement path, safety gate, or CI regression gate.

Safety hardening will use curated, human-reviewed deterministic evidence:

- add a narrowly scoped regex or substring pattern only for a documented
  violation phrasing;
- add a positive regression case, a relevant near-miss where feasible, and an
  expected category label;
- keep response generation and rewriting outside Python; and
- preserve the existing independent structure, vocabulary, and safety-contract
  validator layers.

A future proposal to use a non-deterministic semantic classifier must create an
ADR that explicitly supersedes this one before code, CI, or release behavior
changes. That proposal must explain the safety benefit, deterministic fallback,
privacy handling, reproducibility limits, operating cost, failure reporting, and
rollback behavior.

## Rationale

A deterministic validator gives a reviewer a direct answer to why a response
was rejected. Its inputs, pattern set, match result, tests, and eval fixtures
can all be inspected without an external service. This preserves reproducible
CI and keeps safety enforcement available when no model or network is present.

The response-safety validator is a guardrail, not a response-quality judge. It
must identify enumerated violations before delivery without becoming a second
language model that makes opaque or inconsistent content judgments. Maintaining
that boundary protects SoulMap's knowledge-first architecture and avoids mixing
probabilistic quality scoring into its deterministic regression gate.

The accepted trade-off is that literal rules cannot recognize every unsafe
paraphrase. SoulMap addresses that gap through layered controls and maintenance:
pre-generation routing and safety overrides, independent post-generation
validators, human-reviewed response templates, and regression cases added when
a concrete phrasing gap is observed.

## Alternatives Considered

### Add an LLM classifier to the runtime safety path

Rejected. A model classifier would be non-deterministic, require an external
runtime dependency, complicate failure diagnosis, and make a safety decision
less reproducible. It would also create a new delivery dependency for a layer
that must remain inspectable and fail predictably.

### Add an LLM judge to CI only

Rejected. Moving the model outside the runtime does not make its scores
deterministic. It would turn a regression gate into a quality benchmark with
variable results, cost, and ambiguous failures. Human review may inform future
fixtures, but it is not a CI enforcement mechanism.

### Add broad heuristic scoring without a model

Rejected. Opaque scores and thresholds would be harder to audit than explicit
patterns while still failing to provide true semantic understanding. The current
category-and-pattern contract is clearer and more testable.

### Keep the existing literal contract without further maintenance

Rejected. The contract must remain a maintained safety artifact. Concrete,
human-reviewed phrasing gaps should produce focused pattern and regression
updates, provided they preserve the deterministic boundary.

## Consequences

The current implementation stays dependency-free, reproducible, and suitable
for deterministic local and CI validation. Maintainers must not characterize the
validator as semantic safety understanding or as a complete guarantee against
unsafe paraphrases.

Phase 10 follow-up work focuses on evidence quality rather than model adoption:
maintain category-level positive and near-miss fixtures, keep the safety
enforcement matrix current, and make small deterministic hardening changes only
when justified by a reviewed gap.

This ADR does not change crisis detection, framework selection, response
wording, the safety-gate priority order, or the existing layered crisis
detection decision in ADR 0001.

## References

- [SOULMAP.md](../../../SOULMAP.md#non-negotiable-safety-rules)
- [Known architecture limitations](../known-limitations.md#safety-enforcement-boundaries)
- [Safety enforcement matrix](../safety-enforcement-matrix.md)
- [Issue #132](https://github.com/tuanductran/soulmap-ai/issues/132)
- [ADR 0001](0001-layered-crisis-detection.md)
