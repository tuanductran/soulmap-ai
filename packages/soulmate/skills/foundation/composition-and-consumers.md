---
name: "soulmate-foundation-composition-and-consumers"
description: "Rules for composing Soulmate capabilities through explicit consumer boundaries without transferring framework policy into the foundation."
license: "MIT"
---

# Composition and consumers

## Purpose

This skill defines how a consumer composes Soulmate foundation capabilities while preserving ownership. Soulmate provides small, explicit, inspectable operations. A consuming framework or application decides how those operations are combined, interpreted, routed, presented, and governed for its own product.

Composition is the boundary between a reusable library and an opinionated consumer. It is successful when the foundation remains useful without the consumer and the consumer can use the foundation without importing private state.

## Use this skill when

Use this skill when a framework needs to combine contracts, resource loading, knowledge parsing, text normalization, data validation, or lifecycle stages into a larger operation. Use it when deciding whether a new abstraction belongs in Soulmate or should remain in a consumer adapter.

Use it before extracting a workflow from an existing framework. Identify the neutral operations first, then leave product decisions at the consumer boundary.

## Do not use this skill for

Do not use this skill to define a product's routing hierarchy, response voice, safety doctrine, domain worldview, provider integration, user interface, or deployment policy. Do not use a composition layer to hide those decisions in a supposedly neutral helper.

Do not treat composition as permission to import every foundation module, scan every resource directory, or activate every manifest entry. Consumers must choose their dependencies explicitly.

## Ownership model

The foundation and consumer have different responsibilities:

| Concern | Soulmate foundation | Consumer framework/application |
| --- | --- | --- |
| Contract shape | Defines neutral input, result, invariant, and failure boundaries | Adds product-specific constraints after the foundation boundary |
| Resource access | Validates explicit references and exposes loader seams | Chooses approved resources and access policy |
| Knowledge handling | Parses explicitly supplied neutral content | Decides which knowledge applies and what it means |
| Text handling | Performs declared lexical normalization | Chooses when normalization is useful and how values are displayed |
| Data handling | Parses bounded data and validates basic fields | Defines application schema and domain semantics |
| Lifecycle | Provides ordering guarantees for shared stages | Chooses workflow composition, retries, and user-facing policy |
| Routing | None | Selects framework, mode, route, or handler |
| Safety and policy | Reports contract failures and boundary violations | Applies product safety policy and escalation behavior |
| Presentation | Returns structured results | Produces UI, prompts, messages, or other presentation |

The foundation may expose a result that a consumer considers incomplete. That is preferable to embedding the consumer's interpretation in a shared operation.

## Explicit composition

A composition should declare its capabilities and dependencies in a readable order:

```text
consumer request
    → foundation input contract
    → explicit resource reference
    → resource loader
    → knowledge parser
    → lexical normalization when requested
    → basic data validation
    → foundation result
    → consumer schema and policy
    → consumer presentation
```

Every arrow is a boundary. A consumer must be able to replace one foundation capability with another implementation that satisfies the same public contract. If replacement requires private imports or hidden global state, the composition contract is incomplete.

## Adapter rules

An adapter is appropriate when a consumer's data shape or policy must be translated to a foundation contract. The adapter should be thin and visible.

A good adapter:

- accepts consumer input and constructs explicit foundation input;
- passes approved resources and dependencies through declared seams;
- preserves foundation failures instead of replacing them with ambiguous defaults;
- maps a foundation result into a consumer-owned schema;
- keeps product-specific wording, policy, and routing outside the foundation operation.

An adapter must not alter the meaning of a foundation success or failure merely to make a consumer branch easier. If the consumer needs a different guarantee, define a new contract rather than silently widening the old one.

## Dependency direction

The dependency direction is one-way:

```text
foundation library
        ↑
consumer adapter
        ↑
opinionated framework or application
```

The foundation must not import a consumer package, read consumer configuration, depend on a consumer's resource tree, or call a consumer's router. A consumer may depend on public foundation namespaces, but it must not rely on private foundation implementation details.

A compatibility facade may preserve an older consumer API while delegating to Soulmate. The facade remains consumer-owned and must not become a reason for Soulmate to know about that consumer.

## Policy boundary

A foundation result is not a recommendation about what a product should do. It is a typed or structured observation about the operation that was performed.

For example, a parser may report that a requested section was not found. A consumer may choose to show an empty state, ask for another resource, or apply its own fallback. The foundation must not choose that response and must not encode the product's desired wording in the parser.

The same rule applies to safety, privacy, domain interpretation, and provider selection. Foundation capabilities can expose facts and failures; consumers own action policy.

## Composition and lifecycle

Use the lifecycle skill when a composition has multiple ordered stages. The consumer decides which capabilities are present and whether an optional stage is omitted. It must not claim that a consumer-specific seven-step workflow is a universal foundation lifecycle.

When several operations are composed, each operation should remain testable independently. Add a composition test only for the contract between operations, not as a substitute for unit tests at each boundary.

## Compatibility of composed capabilities

A composition is compatible only when the public contracts of all included capabilities are compatible with the consumer's declared range. A compatible individual skill does not guarantee that every possible combination is valid.

Document required ordering, optional capabilities, result mapping, and failure propagation. If two capabilities can be composed in multiple ways, choose one explicit composition contract rather than relying on import order or directory order.

## Test matrix

A consumer composition should test:

| Case | Expected evidence |
| --- | --- |
| Valid foundation result | Consumer maps it without changing its meaning |
| Foundation input failure | Consumer receives the original category or stable code |
| Resource failure | Consumer does not treat unavailable content as valid content |
| Optional capability omitted | Composition remains valid according to its declared contract |
| Incompatible capability version | Composition fails before activation or packaging |
| Private import attempt | Dependency check rejects the composition |
| Consumer policy mapping | Policy is exercised in consumer tests, not foundation tests |
| Replaced implementation | A contract-compatible substitute can be used in isolation |

## Common anti-patterns

**Foundation-owned routing** makes the library choose which consumer or response mode should run.

**Policy smuggling** hides brand, safety, privacy, or domain rules inside a parser or normalizer.

**Adapter sprawl** moves an entire framework workflow into a wrapper and calls it a neutral composition.

**Failure translation by silence** turns a typed failure into an empty result so the consumer does not need to handle it.

**Private coupling** imports modules or constants that are not part of the public foundation contract.

**Implicit composition** relies on file order, global registration, or directory scanning to decide behavior.

## Review checklist

Before approving a composition, confirm that:

- every included capability is selected explicitly;
- each dependency direction points from consumer to public foundation API;
- foundation results and failures retain their meaning;
- consumer schema, routing, policy, and presentation remain consumer-owned;
- adapters are thin enough to explain in one contract;
- optional stages and ordering requirements are documented;
- the composition can be tested without the full consumer product;
- no directory scan or global registry is required for activation.

## Expected outcome

A completed composition contract lets SoulMap or another future framework build on Soulmate without making Soulmate know about that framework. Soulmate supplies reusable operations; the consumer supplies the product's opinions.
