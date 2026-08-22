---
name: "soulmate-foundation-resource-boundaries"
description: "Explicit, portable resource references and loader boundaries for framework-neutral knowledge systems."
license: "MIT"
---

# Resource boundaries

## Purpose

This skill defines how a foundation library refers to and loads named resources without coupling the reference to a particular application, repository layout, framework, provider, or deployment environment.

A resource boundary separates **what** a consumer wants from **how** the consumer obtains it. The reference identifies one resource. A loader resolves that reference. The foundation contract does not decide which application owns the resource, which route activates it, or how its content is presented.

## Use this skill when

Use this skill when a library needs to name Markdown, text, configuration, or another explicitly approved resource. Use it when a consumer may provide different loaders for a repository, package, archive, memory store, or test fixture while preserving the same reference contract.

Use it before passing filesystem paths through public APIs. Decide whether the path is an explicit repository-relative resource reference or an environment-specific implementation detail.

## Do not use this skill for

Do not use a resource reference as a security policy, a dynamic plugin registry, or a replacement for access control. Do not make a foundation loader discover every file in a directory and activate content implicitly. Do not embed provider URLs, application routes, private credentials, or framework routing decisions in the foundation resource contract.

## Core model

The boundary consists of two concepts:

| Concept | Responsibility |
| --- | --- |
| Resource reference | Holds a non-empty name and a portable relative path |
| Resource loader | Accepts a validated reference and returns UTF-8 content |

The reference is a value, not an open file handle. It should remain safe to inspect, log, compare, and pass between layers without performing I/O.

```text
consumer intent
    ↓
validated resource reference
    ↓
explicit loader selected by the consumer
    ↓
UTF-8 resource content or a loader failure
```

## Reference invariants

A valid resource reference has a non-empty name and a repository-relative path. The name should identify the resource in human-readable terms. The path should be portable across supported operating systems and should not rely on the current working directory being a particular absolute location.

The reference contract rejects an empty or whitespace-only name. It also rejects an absolute path because an absolute path binds a public foundation value to one machine, checkout, user directory, or deployment image.

A relative path is not permission to escape a consumer's root. The loader remains responsible for resolving the path inside its approved root and for rejecting traversal, symlink, archive, or permission conditions according to the consumer's security policy.

## Loader protocol

A loader has one narrow promise: given a validated resource reference, return the resource as UTF-8 text. The loader should not silently select a different resource when the requested one is absent or ambiguous.

A loader implementation may read from a local directory, package resource, archive, or another explicitly approved source. That implementation detail stays outside the reference value and outside the framework-neutral contract.

When a resource cannot be loaded, the loader should expose an inspectable failure that distinguishes at least these cases where relevant:

| Failure | Meaning |
| --- | --- |
| Invalid reference | The reference itself violates the contract |
| Missing resource | The named resource is not present in the approved root |
| Unreadable resource | The resource exists but cannot be read as required |
| Invalid content | The bytes or decoded text do not meet the resource format contract |

The exact error types belong to the public contract of the loader. Callers must not depend on operating-system-specific error prose.

## Authoring workflow

When adding a resource-backed foundation capability:

1. Define the resource type and encoding expected by the consumer.
2. Create a reference with a stable name and portable relative path.
3. Validate the reference before any I/O occurs.
4. Select the loader explicitly; do not discover loaders or resources implicitly.
5. Resolve the reference inside an approved root or package boundary.
6. Decode content with the declared encoding and report failures clearly.
7. Pass the resulting content to a neutral parser or validator.
8. Keep activation, routing, authorization, and presentation in the consuming framework.

## Path portability

Avoid absolute paths in public values, test fixtures, manifests, and examples. A portable relative path uses forward-slash semantics in documentation and manifest data even when a platform uses another native separator internally. The loader may convert separators at the I/O boundary.

Do not assume that a Unix-looking path is absolute on every platform. Cross-platform tests should construct an absolute path from the platform's current working directory when they need to verify rejection of absolute paths.

A loader should resolve a relative reference against an explicit root supplied by the caller, not against an undocumented process-wide current directory. This makes tests reproducible and prevents a caller from accidentally loading a similarly named resource from an unrelated checkout.

## Content ownership

A resource reference does not establish ownership. The manifest or consumer contract must still identify who maintains the resource, which consumers may use it, and which artifact may ship it.

A resource is eligible for a framework-neutral foundation artifact only when its meaning remains valid without a product's brand, voice, routing hierarchy, safety policy, or domain-specific worldview. If the resource exists to tell one product how to behave, it belongs to that product even when it is stored as Markdown.

## Security and determinism checklist

Before approving a loader or resource entry, verify that:

- the reference name is non-empty and stable;
- the path is relative, portable, and resolved beneath an explicit approved root;
- traversal and symlink behavior are defined by the loader;
- the loader does not execute resource content;
- encoding and maximum size expectations are documented;
- missing and unreadable resources produce inspectable failures;
- resource selection is explicit rather than directory-wide discovery;
- ownership, consumer compatibility, and artifact inclusion are declared;
- the same reference and root produce the same result in a clean test environment.

## Common anti-patterns

**Global path lookup** hides the resource root and makes behavior depend on the process environment.

**Implicit discovery** turns a directory into an undocumented plugin system and can change behavior when an unrelated file is added.

**Absolute manifest paths** make artifacts non-portable and reveal local checkout details.

**Silent fallback** can return the wrong resource while appearing successful. If a fallback is part of a consumer policy, it must be explicit, observable, and tested outside the foundation reference itself.

**Executable resources** violate the boundary. Foundation resources are data; loaders return data and do not execute it.

## Expected outcome

A completed resource boundary lets different frameworks supply different storage and loading implementations while sharing the same validated reference semantics. The foundation remains portable and deterministic, while the consumer retains ownership of discovery policy, permissions, activation, and presentation.
