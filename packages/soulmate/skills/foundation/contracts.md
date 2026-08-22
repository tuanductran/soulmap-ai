---
name: "soulmate-foundation-contracts"
description: "Framework-neutral contracts for explicit inputs, resources, results, and inspectable failures."
license: "MIT"
---

# Foundation contracts

## Purpose

This skill defines the minimum contract discipline for a framework-neutral foundation library. A contract is a stable agreement about the shape, meaning, validation, and failure behavior of an operation. Contracts make capabilities reusable because a consuming framework can depend on observable behavior rather than private implementation details.

This skill describes neutral boundaries only. It does not define a product persona, response doctrine, routing hierarchy, safety policy, provider integration, or user-facing behavior.

## Use this skill when

Use this skill when designing or reviewing a public foundation capability that will be consumed by more than one framework, application, or tool. It is especially useful when an operation accepts structured input, resolves a named resource, returns a typed result, or must expose predictable validation failures.

Use it before extracting code from an opinionated framework. First identify the smallest stable promise that can stand without the framework's brand, routing rules, domain policy, or private state.

## Do not use this skill for

Do not use this skill to decide how a product should speak, which workflow should win, which safety policy should apply, or which domain-specific knowledge should be activated. Those are consumer decisions. Do not turn a contract into a general-purpose abstraction merely because two implementations look similar; the behavior must be stable, independently useful, and owned by the foundation.

## Contract model

A public contract has five parts:

| Part | Required meaning |
| --- | --- |
| Input | What values are accepted, including required fields and units |
| Invariants | What must always be true after validation |
| Operation | What deterministic work the capability performs |
| Result | What a successful caller receives and how it is interpreted |
| Failure | Which invalid states are rejected and how callers can inspect them |

A contract is incomplete when it documents only a function name or data shape. Consumers also need the boundary conditions and failure semantics.

## Foundation contract categories

The initial Soulmate foundation uses the following categories:

| Category | Role |
| --- | --- |
| Resource reference | Names one explicitly selected resource without embedding a loader or product policy |
| Resource loader protocol | Defines how a consumer obtains UTF-8 content for a validated reference |
| Knowledge parser | Converts explicitly supplied neutral text into structured phrases or groups |
| Text utility | Performs deterministic lexical normalization without translation or semantic inference |
| Data utility | Parses bounded JSON and validates basic mapping fields without owning an application schema |

These categories are intentionally small. A consumer may compose them into a larger workflow, but composition belongs to the consumer unless the lifecycle itself becomes a proven shared capability.

## Public-surface rules

A foundation contract should satisfy all of the following rules:

- It has a name that describes behavior rather than a product or provider.
- It accepts explicit values instead of reaching into global application state.
- It is deterministic for the same input and configuration.
- It has no requirement for an LLM, network, database, account, or framework runtime.
- It exposes stable public types or protocols instead of private constants.
- It rejects invalid input at the boundary with an inspectable error.
- It does not silently translate, classify meaning, infer intent, or select a consumer policy.
- It can be tested without loading an opinionated framework.

## Authoring workflow

When adding or extracting a foundation contract, follow this order:

1. State the behavior in one sentence without naming a consuming product.
2. List the smallest accepted input and every required invariant.
3. Define the successful result in terms a different implementation could reproduce.
4. Define invalid input and the error category or message callers may rely on.
5. Check that the contract has no hidden dependency on brand, routing, policy, or private state.
6. Add a focused contract test for success, boundary values, and each important failure.
7. Add a consumer integration test only after the foundation contract is independently stable.
8. Record ownership and compatibility in the skill manifest before shipping the capability.

## Error boundaries

Errors should identify the violated contract, not expose incidental implementation details. A caller should be able to distinguish invalid input from an unavailable resource and from an unexpected internal failure.

Do not use a successful empty result to conceal malformed input when the contract requires a value. Conversely, do not reject an omitted optional value when the contract explicitly defines a neutral default. The distinction between required, optional, and empty values must be documented.

Error messages may be human-readable, but callers should not be required to parse fragile prose when a typed error category or stable error code is available. Adding a new error category is a compatibility decision and must be reviewed like any other public change.

## Composition rules

Foundation contracts compose from the outside in:

```text
explicit input
    ↓
contract validation
    ↓
neutral operation
    ↓
inspectable result or failure
    ↓
consumer-specific policy and presentation
```

The foundation must stop before consumer-specific policy. A library may report that a value is invalid; it must not decide what an application should say or do in response to that invalid value.

## Review checklist

Before approving a contract, confirm that:

- another framework could implement or consume it without adopting the original product's worldview;
- the contract can be exercised offline with fixed inputs;
- success and failure behavior are documented and tested;
- optional defaults do not hide malformed required data;
- no private module, global registry, or implicit directory scan is part of the promise;
- the name, owner, version, and consumers are recorded in the manifest;
- the contract is smaller than the first consumer's complete workflow.

## Expected outcome

A completed contract skill gives a future framework a stable foundation seam. The consumer remains responsible for orchestration, domain decisions, policy, presentation, and user experience. The foundation remains useful even when no consumer framework is installed.

## Boundary reminder

A capability belongs in the foundation only when its behavior is both **framework-neutral** and **independently valuable**. If removing a product name makes the rules meaningless, the capability belongs to that product instead.
