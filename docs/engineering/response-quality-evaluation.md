# Response Quality Evaluation Contract

This document defines the boundary between SoulMap response-quality evaluation
and deterministic safety enforcement.

## Purpose

`uv run soulmap eval-response-quality` evaluates generated/reference response
quality with deterministic rubric checks. It covers:

- selected-framework adherence
- mirror-first / non-advice posture
- user ownership
- response shape
- tone and voice alignment
- epistemic framing where a case requires it
- independence and non-dependency language

The evaluator also reports the existing deterministic response-safety contract
for the same cases, but the two results remain separate.

## Fixtures

The evaluator uses two fixture surfaces:

1. `evals/datasets/response_generation_cases.json` supplies the representative
   positive cases and primary framework coverage.
2. `evals/datasets/response_quality_cases.json` supplies explicit negative and
   near-miss responses, including cases where quality fails while safety passes
   and cases where safety fails while quality passes.

The response-generation dataset covers every primary framework family:
`DE_ESCALATION`, `MIRROR`, `CRISIS`, `DEPENDENCY`, `GRIEF`, `EXISTENTIAL`,
`INNER_PARTS`, `DIRECTION`, `SHADOW`, `MEANING_INTEGRATION`, and `SYNTHESIS`.

## Determinism

The evaluator performs local regex/substring and structural checks only. It
uses no LLM judge, network request, user conversation, or probabilistic score.
The same repository state and fixture data therefore produce the same result.

If an LLM judge is introduced in the future, its model/version, prompt,
reproducibility limits, cost, and false-positive handling must be documented
separately and it must remain outside runtime safety enforcement.

## Safety boundary

Safety is not inferred from the quality score. The deterministic safety
contract remains the release-blocking signal. A quality failure is advisory and
must not be treated as a safety incident by itself. Conversely, a response may
pass the quality rubric while failing the safety contract and must still be
rejected or rewritten by the safety path.

CI runs the quality evaluator with `continue-on-error: true` and uploads its
JSON report as an artifact. Existing deterministic safety evaluations remain
blocking.

## Command

```bash
uv run soulmap eval-response-quality
```

Exit code `0` means all advisory quality fixtures and safety expectations in
the fixture set match. Exit code `1` identifies a quality or fixture mismatch;
CI does not promote that result into a release blocker.

## Non-goals

- replacing deterministic runtime safety enforcement
- generating or rewriting responses in Python
- adding an LLM dependency to CI
- using real user conversations as evaluation data
- turning quality scores into product behavior or user profiling
