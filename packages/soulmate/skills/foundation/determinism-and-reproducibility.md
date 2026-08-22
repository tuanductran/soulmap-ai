---
name: "soulmate-foundation-determinism-and-reproducibility"
description: "Determinism and reproducibility rules for Soulmate foundation operations and independently generated skill artifacts."
license: "MIT"
---

# Determinism and reproducibility

## Purpose

This skill defines how a Soulmate capability or generated artifact can make repeatable behavior claims. Determinism concerns whether the same declared inputs produce the same observable result. Reproducibility concerns whether the same declared source and build inputs can recreate the same artifact or verification outcome.

Neither claim is meaningful when hidden state, ambient environment, undeclared network access, or undocumented selection rules can change the result.

## Use this skill when

Use this skill when a foundation capability claims stable output, when tests compare exact results, when a manifest selects files for distribution, or when a build must be recreated in a clean environment.

Use it before adding caches, timestamps, randomness, network access, concurrency, locale-sensitive behavior, or environment-dependent file discovery to a shared capability.

## Do not use this skill for

Do not use this skill to promise identical behavior from an external AI provider, model, operating system, browser, network service, or consumer product unless those dependencies are controlled and included in the declared inputs.

Do not remove meaningful metadata merely to make two artifacts byte-identical. If a timestamp, build identity, or platform marker is required, declare it and define what level of reproducibility is claimed.

## Determinism model

A deterministic operation is defined by its declared inputs and configuration:

```text
observable result = operation(explicit input, explicit configuration, explicit resources)
```

A claim of determinism must state what is held constant. It should not depend on current time, random state, process order, locale defaults, current working directory, ambient environment variables, network responses, global registries, or directory enumeration order unless those values are explicit inputs.

Determinism does not require that every implementation use the same internal algorithm. It requires that implementations satisfying the contract produce equivalent observable results for the declared input domain.

## Sources of nondeterminism

Review these sources before making a stability claim:

| Source | Safer foundation rule |
| --- | --- |
| Time | Pass time as an explicit input or exclude time from the result |
| Randomness | Pass a seed or do not claim deterministic output |
| Locale | Declare locale and normalization policy explicitly |
| Filesystem order | Sort paths and select through a manifest |
| Network | Keep network out of the foundation or record response as explicit input |
| Environment | Declare relevant variables and use a controlled baseline |
| Concurrency | Define ordering or avoid relying on completion order |
| Global state | Pass configuration and dependencies through the public seam |
| Caches | Treat cache behavior as an optimization, not a semantic input |
| Serialization | Define encoding, key ordering, whitespace, and newline rules |

A deterministic capability may use an implementation cache if the cache cannot change the result, failure category, or selected resource.

## Reproducible source selection

A reproducible artifact begins with a reproducible source set. Use a validated manifest and explicit allow-list. Do not include files based on directory traversal order, modification time, ignored-file state, or whichever files happen to be present in a local checkout.

Paths should be normalized to portable relative form, sorted before packaging, and checked against the approved root. A clean staging directory prevents stale content from becoming an undeclared build input.

## Reproducible build levels

Record the level of evidence being claimed:

| Level | Claim |
| --- | --- |
| Source-set reproducibility | The same manifest resolves to the same ordered source file list |
| Content reproducibility | Selected source contents and metadata match the expected digests |
| Functional reproducibility | Clean builds produce artifacts with equivalent extracted content and behavior |
| Byte reproducibility | Clean builds produce byte-identical artifacts under a controlled toolchain |

A lower level is still useful. Do not claim byte reproducibility when only extracted content parity has been tested.

## Artifact controls

A reproducible Soulmate skill artifact should control or record:

- manifest schema and library identity;
- selected skill IDs and content versions;
- ordered source file list;
- text encoding and newline policy;
- package/build tool versions;
- source commit or other build input identity;
- output file naming and version rules;
- archive path ordering and metadata policy; and
- verification and digest results.

Generated timestamps should be fixed, omitted, or explicitly treated as non-semantic metadata according to the claimed level. A digest proves bytes for one output; it does not prove that the source selection was correct.

## Test design

Use fixed inputs and isolated temporary directories. A useful reproducibility test builds or executes the same operation more than once and compares the claimed observable surface.

For a capability, compare result shape, values, ordering, and failure category. For an artifact, compare manifest, extracted file list, selected content, versions, and digests. If platform-specific metadata is expected, compare the platform-neutral surface separately from platform-specific output.

Tests should also perturb irrelevant ambient conditions where practical. Changing current working directory, file creation order, unrelated files, or process environment must not change a capability that does not declare those values as inputs.

## Failure evidence

When reproducibility fails, report the first differing boundary and preserve enough information to investigate:

| Evidence | Purpose |
| --- | --- |
| Declared inputs | Shows what the operation was supposed to depend on |
| Environment baseline | Explains toolchain and platform context |
| Ordered file list | Detects selection/order drift |
| Content/digest comparison | Locates changed bytes |
| Verification output | Shows which contract failed |
| Build command/configuration | Allows a clean reproduction |

Failure evidence must not include credentials, complete untrusted payloads, or private machine paths when a redacted identifier is sufficient.

## Relationship to caches and increments

Incremental builds may reuse a verified result only when the cache key covers every semantic input and the cached output is itself validated. A cache hit must not bypass boundary verification.

A cache is not a source of truth. If the cache is missing, stale, corrupt, or built under an incompatible toolchain, a clean build must remain possible.

## Relationship to consumers

Soulmate can guarantee deterministic lexical, parsing, validation, and selection behavior within its declared input domain. A consumer may add time, user state, provider calls, model sampling, or product policy after the foundation result. Those additions change the consumer's reproducibility claim and must not be described as a guarantee of the foundation library.

A consumer can still build a reproducible composition by declaring those additional inputs and controlling the relevant environment. The declaration belongs to the consumer composition contract.

## Common anti-patterns

**Ambient-time dependence** changes output based on the current clock without declaring time.

**Unsorted selection** makes file or result order depend on the filesystem or process scheduler.

**Environment leakage** lets locale, working directory, or undocumented variables alter a foundation result.

**Cache authority** treats a cached artifact as canonical and skips verification.

**Hash overclaim** treats one digest as proof of correct source ownership or semantic equivalence.

**Byte-identity overclaim** calls extracted-content parity byte reproducibility without controlling archive metadata.

**Consumer leakage** promises reproducibility for provider/model behavior that the foundation does not control.

## Review checklist

Before approving a determinism or reproducibility claim, confirm that:

- declared inputs and configuration are complete;
- time, randomness, locale, filesystem order, network, environment, concurrency, and global state were considered;
- source selection is manifest-driven and ordered;
- the clean staging path is reproducible;
- the evidence level is named accurately;
- caches do not bypass verification;
- tests compare the correct observable surface;
- failure evidence is actionable without leaking sensitive data;
- consumer-only nondeterminism is not attributed to Soulmate.

## Expected outcome

A completed determinism and reproducibility contract lets Soulmate make precise stability claims without pretending that every consumer environment is identical. It supports reliable foundation operations and auditable artifact builds while keeping external provider and product behavior outside the library guarantee.
