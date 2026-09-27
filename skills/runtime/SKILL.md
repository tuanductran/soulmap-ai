---
name: "runtime"
description: "SoulMap runtime integration contracts for the Python layer. Use only to connect executable runtime components to shipped Markdown knowledge; domain knowledge remains in the domain skill folders."
version: "0.12.1"
license: Complete terms in LICENSE
---

# SoulMap runtime integration layer

This folder is the only shipped Markdown layer that describes how the Python runtime
locates and consumes SoulMap knowledge.

## Boundary

Domain skills own meaning, language, frameworks, signals, and guidance. Runtime
integration files own the machine-facing mapping needed to load that knowledge.

Python runtime code must not embed a repository path to a domain Markdown file.
Instead, it resolves a stable source identifier through [source-registry.md](source-registry.md).

The registry is not a second knowledge base. It is a routing contract.

## Rules

- Keep domain content implementation-neutral.
- Keep Python source paths, module names, code examples, and repository-only implementation details out of domain skills.
- Change a Markdown source location in this registry rather than editing detector path literals.
- Do not copy domain guidance into Python.
- Do not move safety-critical hardcoded crisis language into this layer without an explicit architecture decision and full safety validation.

## References

- [source-registry.md](source-registry.md): canonical Python-to-Markdown source mapping.
- [SOULMAP.md](../../SOULMAP.md): behavioral doctrine.
