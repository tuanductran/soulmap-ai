---
name: "soulmate-foundation-lifecycle"
description: "A framework-neutral lifecycle for validating input, resolving resources, executing a capability, and returning an inspectable result."
license: "MIT"
---

# Foundation lifecycle

## Purpose

This skill defines a small lifecycle for a foundation capability. It gives a consumer a predictable order for accepting input, validating boundaries, resolving explicitly selected resources, executing one capability, validating the result, and returning success or failure.

The lifecycle is a coordination contract, not a product workflow. It does not select a domain framework, classify a user's emotional state, apply a brand voice, enforce a product safety policy, choose a route, or generate a user-facing response.

## Use this skill when

Use this skill when a capability has more than one boundary operation and different consumers need the same ordering guarantees. It is useful for a resource-backed parser, a deterministic transformation, a structured-data operation, or another offline foundation task with observable success and failure states.

Use it when a consumer needs to know which work has happened before a result is trusted. Keep the lifecycle as small as the shared guarantee requires; do not introduce stages that exist only for one framework.

## Do not use this skill for

Do not use this skill as an implicit plugin runner, application router, request server, conversation policy, safety pipeline, or response-generation recipe. Do not use it to prescribe how a consumer interprets a result or what a product says after a failure.

Do not force a capability into every stage. A simple pure transformation may need only input validation, execution, and result validation. The lifecycle is composable; it is not a requirement to add ceremony around a small operation.

## Lifecycle model

The neutral lifecycle has six conceptual stages:

| Stage | Responsibility | Required boundary |
| --- | --- | --- |
| Define | Identify the capability and its explicit input/configuration | The operation has a stable name and declared contract |
| Validate input | Check required values, types, limits, and invariants | Invalid input stops before side effects or resource work |
| Resolve | Obtain explicitly selected resources or dependencies | Resolution is observable and stays within approved boundaries |
| Execute | Perform the capability's neutral operation | Work uses only validated input and resolved dependencies |
| Validate result | Check the result shape and core invariants | Invalid results are not reported as success |
| Finalize | Return a result or inspectable failure to the consumer | Consumer policy begins only after the foundation result exists |

The stages form an order, not a set of hidden callbacks:

```text
explicit capability + input
          ↓
     input validation
          ↓
  explicit resource resolution
          ↓
    neutral capability work
          ↓
     result validation
          ↓
 result or inspectable failure
          ↓
 consumer-specific policy
```

A capability may omit `Resolve` when it has no resource or external dependency. It may combine `Define` with a public operation when its identity is already fixed by the contract. Any omitted stage must be intentional and documented.

## Stage invariants

### Define

The capability name, version, accepted input, configuration, output, and failure behavior must be known before execution. A consumer must not need to inspect private implementation details to understand what operation is being requested.

The definition must not include a hidden route, global registry, product persona, provider credential, or implicit filesystem location.

### Validate input

Input validation happens before resource resolution and before operation-specific side effects. The validator checks structure and contract invariants, not domain meaning that belongs to the consumer.

Validation must be deterministic. If a value is invalid, the lifecycle returns an inspectable failure instead of continuing with a best-effort interpretation. Optional defaults must be explicit; a missing required value must not become an empty success by accident.

### Resolve

Resolution is explicit. The consumer or a declared adapter supplies the resource reference or dependency boundary. The lifecycle must not discover arbitrary files, choose among ambiguous providers, or silently replace a missing resource with an unrelated one.

A resolution failure is different from invalid input and should remain distinguishable when the public contract requires that distinction. Resolved data is still untrusted input to the execution stage and may require content or size validation.

### Execute

Execution performs only the neutral capability promised by the contract. It should not mutate unrelated global state, change routing, publish an artifact, send a network request, or apply consumer policy unless that side effect is explicitly part of a separate approved contract.

The same validated input and configuration should produce the same result for a deterministic capability. If an operation intentionally depends on time, randomness, network state, or external state, that dependency must be explicit and the operation is not automatically eligible for the smallest deterministic lifecycle.

### Validate result

Result validation protects the boundary in both directions. It confirms that successful execution returned the type, shape, limits, and invariants promised to consumers.

A result validator must not rewrite a semantically invalid result into an apparently valid one. If a consumer requires additional domain validation, it applies that validation after receiving the foundation result.

### Finalize

Finalization returns either the validated result or an inspectable failure. It does not decide how a framework should display, route, retry, apologize, escalate, or explain the outcome.

A consumer may map foundation failures into its own policy, but that mapping must remain outside the foundation lifecycle and must not change the meaning of the original failure.

## Failure and cancellation

A lifecycle should stop at the earliest stage that can identify a contract failure. Later stages must not run after an invalid input, unresolved required dependency, or invalid intermediate result.

Cancellation is a boundary event, not a successful empty result. If a consumer supports cancellation, the cancellation signal and its ownership must be explicit. Cleanup must not hide the original failure or produce a misleading success.

Failures should preserve enough context to identify the stage and violated contract without including secrets, complete untrusted payloads, or private filesystem details. Callers should not need to parse unstable human-readable prose to distinguish categories when typed errors or stable codes are available.

## Idempotency and side effects

A pure or deterministic foundation operation should be safe to retry with the same validated inputs. If it writes, caches, increments, publishes, or otherwise mutates state, that side effect must be declared by the operation contract and tested separately.

Do not add retries to the generic lifecycle by default. Retry policy depends on the consumer, failure type, idempotency guarantee, and operational context. A foundation lifecycle can report a failure; it should not guess whether repeating work is safe.

## Composition rules

A larger consumer workflow may compose multiple foundation capabilities:

```text
validate request
    → resolve resource
    → parse content
    → normalize lexical values
    → validate consumer schema
    → apply consumer policy
```

Composition must preserve ownership. The foundation can provide the first four neutral operations. The consumer owns schema interpretation, routing, policy, presentation, and any user-facing behavior.

One capability must not call a hidden global pipeline merely because it is used by a framework. Dependencies should be passed through an explicit seam so that the foundation remains testable without the consumer installed.

## Authoring workflow

When adding a lifecycle-backed capability:

1. Write the capability contract before choosing stages.
2. Mark which stages are required and which are intentionally omitted.
3. Validate input before I/O, mutation, or expensive work.
4. Make resources and dependencies explicit.
5. Keep execution limited to the neutral operation.
6. Validate the result before returning success.
7. Preserve failure stage and category without leaking sensitive data.
8. Define cancellation and retry ownership outside the generic lifecycle.
9. Add tests for success, each boundary failure, stage ordering, and no-work-after-failure.
10. Record the capability and consumer compatibility in the skill manifest.

## Test matrix

A lifecycle contract should have focused evidence for:

| Case | Expected evidence |
| --- | --- |
| Valid input, no resource | Execution occurs and result validates |
| Missing required input | Resolution and execution do not occur |
| Invalid input type or limit | Failure identifies the input boundary |
| Missing resource | Execution does not occur and resolution failure is inspectable |
| Invalid resource content | Content failure is not reported as a successful result |
| Capability failure | Failure is preserved without false success |
| Invalid result | Finalization rejects the result |
| Cancellation | Operation stops according to the declared cancellation contract |
| Repeated deterministic call | Same input/configuration gives the same result |

## Common anti-patterns

**Framework pipeline leakage** embeds one consumer's routing, safety, voice, or response stages in a shared lifecycle.

**Implicit discovery** makes adding a file or package change behavior without a manifest or explicit consumer choice.

**Validate-after-execute** permits malformed input or invalid output to cross the public boundary.

**Generic retry behavior** repeats work without knowing whether the operation is idempotent.

**Failure swallowing** converts a failed stage into an empty or default success.

**Lifecycle inflation** adds stages that no independent consumer needs and turns a small capability into an unmaintainable framework.

## Review checklist

Before approving a lifecycle capability, confirm that:

- every stage exists for a shared, documented reason;
- input, resource, execution, result, and failure boundaries are explicit;
- no stage owns product routing, safety, voice, brand, or domain policy;
- failure stops later work where required;
- cancellation and retry ownership are declared rather than guessed;
- deterministic behavior is tested when claimed;
- side effects are explicit and not hidden in a neutral helper;
- a framework can consume the result without importing private foundation state.

## Expected outcome

A completed lifecycle skill gives consumers a reliable order of neutral operations without turning Soulmate into an opinionated application framework. Soulmate validates and executes foundation capabilities; the consumer decides what those results mean and how its product should respond.
