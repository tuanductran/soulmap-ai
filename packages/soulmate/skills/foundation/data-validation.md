---
name: "soulmate-foundation-data-validation"
description: "Bounded JSON parsing and basic mapping validation for framework-neutral data boundaries."
license: "MIT"
---

# Data validation

## Purpose

This skill defines a small and predictable boundary for accepting JSON data. It separates parsing from application-specific validation so that a foundation library can reject malformed or structurally unsuitable input without deciding what a consuming framework's domain model should mean.

The initial foundation capability supports bounded JSON objects and arrays, basic mapping field checks, and explicit defaults for optional fields. It does not define a product schema, a database model, a network protocol, or a semantic validation policy.

## Use this skill when

Use this skill when a consumer receives raw JSON text and needs to establish that the payload is valid JSON of an allowed top-level shape before further processing. Use it when a small shared helper can enforce byte limits and basic field types consistently across multiple consumers.

Use it before passing untrusted or externally supplied text into a consumer-specific schema validator. The foundation boundary should be early, explicit, and easy to test offline.

## Do not use this skill for

Do not use this skill as a complete schema language, business-rule validator, authorization layer, API gateway, database validator, or semantic classifier. Do not infer missing values, coerce arbitrary types, accept malformed JSON as a partial result, or decide whether a domain value is safe or appropriate.

Do not add application-specific fields to the foundation helper merely because one consumer uses them. A field belongs in a consumer schema unless its type and behavior are demonstrably shared and stable.

## Accepted top-level values

The foundation distinguishes two parsing operations:

| Operation | Accepted top-level JSON value | Result |
| --- | --- | --- |
| Object parsing | JSON object only | Mapping from string keys to values |
| Value parsing | JSON object or JSON array | Object-or-array union |

JSON scalars such as strings, numbers, booleans, and `null` are rejected by these operations. A consumer that needs a scalar must define a separate, explicitly named contract rather than weakening an existing object-or-array boundary.

## Input bounds

Raw input must be present. An empty string is rejected before JSON decoding. Input size is measured after UTF-8 encoding, not by the number of Python characters or visual glyphs.

The default maximum is 200,000 UTF-8 bytes. A consumer may provide another explicit maximum or disable the limit only when that choice is part of its own reviewed contract. Limits protect predictable memory use and prevent an apparently valid parser call from accepting unbounded input.

An input over the configured limit is rejected before JSON decoding. The failure should identify the observed byte count and configured limit without echoing the complete input.

## Parse behavior

JSON decoding must be strict enough to distinguish malformed input from valid data. A decoding failure is reported as a parse failure with the underlying location available for diagnosis, but callers should not depend on a particular JSON implementation's full prose.

After decoding, the top-level type is checked explicitly. A valid JSON document with an unsupported top-level type is still a contract failure.

The parser returns decoded values; it does not recursively certify every nested value against an application schema. Consumers remain responsible for nested structures, permitted keys, business rules, and domain semantics.

Conceptually:

```text
raw UTF-8 text
    ↓
presence and byte-limit check
    ↓
JSON decoding
    ↓
top-level shape check
    ↓
object/array result or inspectable failure
    ↓
consumer-specific schema validation
```

## Field validation

Basic field helpers make a narrow distinction between optional defaults and required values:

| Field rule | Behavior |
| --- | --- |
| String with default | Missing field returns an empty string; a present non-string fails |
| Non-empty required string | Missing or empty field fails; a present non-string also fails |
| List with default | Missing field returns an empty list; a present non-list fails |
| Object with default | Missing field returns an empty object; a present non-object fails |

These helpers validate the immediate field type only. They do not trim, normalize, translate, coerce, deduplicate, validate nested members, or apply domain rules unless a separate consumer contract says so.

An empty string is not automatically equivalent to a missing field. A consumer must choose between an optional default and a required non-empty field explicitly.

## Authoring workflow

When adding a JSON-backed foundation capability:

1. Define the smallest top-level shape required by more than one consumer.
2. Set an explicit byte limit and document why it is appropriate.
3. Parse raw text before applying field-level rules.
4. Validate required fields without silently coercing values.
5. Keep nested schema and domain checks in the consuming layer.
6. Add tests for empty input, invalid JSON, oversized UTF-8 input, unsupported scalars, valid objects, valid arrays, wrong field types, missing required fields, and optional defaults.
7. Version a contract when a previously accepted shape or failure behavior changes.

## Error boundaries

A caller should be able to distinguish at least these failures:

- no input was provided;
- the UTF-8 byte limit was exceeded;
- JSON syntax was invalid;
- the top-level JSON shape was unsupported;
- a field had the wrong type;
- a required non-empty field was absent or empty.

The initial implementation may use a common value-error family for these deterministic validation failures, but the message should identify the violated boundary. A future typed error hierarchy must preserve the ability to diagnose these categories without requiring callers to parse unstable text.

Validation failures must not include secrets or reproduce a large untrusted payload. They should be safe to record in a test report or structured log.

## Determinism and compatibility

For the same raw input and the same byte limit, parsing produces the same result or the same category of failure. The operation does not depend on locale, network state, filesystem state, current time, random state, or application registries.

Changing the default byte limit, accepted top-level types, field defaults, or error categories is a compatibility change. Such a change requires a focused regression test and a manifest/package version decision when it affects public consumers.

## Common anti-patterns

**Type coercion** turns malformed input into plausible but untrusted data.

**Schema leakage** places a single framework's domain fields in a shared helper.

**Character-count limits** mismeasure UTF-8 payload size and can disagree across clients.

**Silent scalar acceptance** weakens an object contract without making the API name or consumer expectations clear.

**Deep validation in the parser** makes a generic utility own domain policy and prevents reuse.

**Echoing raw payloads in errors** can leak secrets or create oversized logs.

## Review checklist

Before approving a data boundary, confirm that:

- empty input is rejected explicitly;
- the limit is measured in UTF-8 bytes;
- JSON syntax and top-level shape are checked separately;
- optional defaults and required fields are distinguishable;
- wrong types are rejected rather than coerced;
- nested and domain validation remain in the consumer;
- failures are inspectable without exposing raw payloads;
- deterministic success and negative cases are tested;
- changes to accepted shapes or limits are versioned and reviewed.

## Expected outcome

A completed data-validation contract gives multiple frameworks a consistent first boundary for JSON text while preserving consumer ownership of schemas and domain meaning. The foundation handles structure and bounded input; the consumer handles interpretation and policy.
