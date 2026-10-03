# ADR 0006: Layered Skill Resources for Content, Examples, and Prompt Orchestration

## Status

Accepted

## Context

SoulMap's shipped Skill currently has one root `SKILL.md` entrypoint and a
canonical knowledge tree under `skills/`. Individual framework files already
mix several concerns: domain knowledge, worked language examples, response
constraints, and references to other knowledge files.

A proposed resource model separates those concerns inside a logical Skill
package:

```text
<skill>/
├── content/
├── examples/
└── prompt/
```

The intent is not to create additional Skill entrypoints. The root
`SKILL.md` remains the single shipped entrypoint.

A feasibility review of the current repository found that the package builder
already includes every regular file below `skills/`. No packager change is
therefore required merely to ship these resource directories. The extracted
artifact contract also validates the actual package member set, so a future
implementation can be tested against the same source-of-truth boundary.

The current knowledge base demonstrates the need for clearer ownership. For
example, `relationship-reflection.md` contains framework knowledge, worked
prompt-like language, response constraints, and links to shared response
guidance in one file. This is useful today, but it makes it harder to
distinguish reusable knowledge from demonstrations and orchestration
instructions.

## Decision

Propose the following resource semantics for future Skill restructuring:

| Resource | Meaning | Primary question |
| --- | --- | --- |
| `content/` | Canonical knowledge specific to the Skill | What does this Skill know? |
| `examples/` | Worked demonstrations and representative situations | How does that knowledge look when applied? |
| `prompt/` | Skill-level orchestration and usage instructions that reference the other resources | How should the Skill use its knowledge and examples? |

These resources are complementary rather than duplicated:

- `content/` owns factual, conceptual, framework, and behavioral knowledge.
- `examples/` demonstrates application and must not become a collection of
  canned answers to copy verbatim.
- `prompt/` owns orchestration instructions and references canonical resources;
  it must not copy the full contents of `content/` or `examples/`.
- The root `SKILL.md` remains responsible for Skill identity, activation,
  top-level routing, and package-level instructions.
- Shared SoulMap doctrine and safety remain authoritative in their existing
  canonical locations. This proposal does not create per-Skill copies of
  global safety doctrine.

The directories are optional by need. A Skill does not need all three resource
types merely to satisfy a filesystem convention.

The model should be introduced incrementally. Existing Markdown should not be
mass-moved or duplicated until a concrete Skill demonstrates that the separation
improves authoring, progressive disclosure, or response quality.

## Rationale

### Knowledge-first architecture

The model keeps behavior-defining material in Markdown. It does not introduce
a response generator, executable Skill runtime, or second routing engine.

### Single ownership question

The current framework files can contain knowledge, examples, and instructions
together. Explicit resource roles make future review easier: a maintainer can
ask whether a new paragraph belongs to knowledge, demonstration, or
orchestration before adding it.

### Progressive disclosure

An AI tool can load the Skill entrypoint first, then the Skill-level prompt,
then only the relevant content and examples. This can reduce unnecessary
context without requiring a Python selector.

### Packaging compatibility

The current package builder recursively includes files under `skills/`. The
resource directories therefore fit the existing distribution boundary. The
important contract is that all references between shipped resources remain
resolvable after extraction.

## Alternatives Considered

### Keep one Markdown file per framework

This is the current model. It has the lowest migration cost, but it leaves
knowledge, demonstrations, and orchestration mixed when a framework becomes
large.

### Add executable `scripts/` to each Skill

This can support deterministic resource selection, but it introduces an
additional execution surface and creates pressure to reproduce routing or
response behavior outside the canonical knowledge layer. It is not required
for this resource-separation proposal.

### Put all Skill-specific material into one large prompt

This would make the prompt a second copy of the knowledge base. It creates
duplication and makes drift likely, so it is explicitly rejected.

## Consequences

### Positive

- Clearer separation between knowledge, demonstrations, and orchestration.
- Better support for progressive disclosure.
- No new executable runtime is required.
- Existing package discovery already supports the directory shape.
- The model can be adopted per Skill instead of requiring a repository-wide
  migration.

### Negative

- A poorly designed migration could create duplicate canonical knowledge.
- Resource boundaries will require authoring and contract guidance.
- Existing cross-links will need careful preservation when a large framework is
  decomposed.

### Acceptance evidence

The implementation decision is now accepted based on two isolated repository spikes:

1. PR #561 decomposed the non-detector-backed `relationship-reflection` framework into `content/`, `examples/`, and `prompt/` without introducing a second Skill entrypoint, runtime, or duplicated global doctrine.
2. PR #562 decomposed the larger runtime-backed `shadow-patterns` framework, including its detector-loaded canonical source, supporting `self-compassion` source, downstream evals, tests, and integration references.
3. Both spikes preserved Markdown link and packaging contracts. PR #562 initially exposed a stale relative link through CI; the link was corrected and the complete required CI matrix then passed.
4. The prompt resources reference canonical content and examples instead of copying them, while examples are explicitly demonstrations rather than canned responses.
5. The existing recursive package boundary required no packager redesign. The successful PR #562 build and knowledge-audit runs provide repository-level evidence that the layered resources remain inside the shipped knowledge boundary.
6. The two decompositions demonstrate clearer authoring ownership and enable progressive disclosure: orchestration can reference examples optionally while runtime-backed consumers continue loading only the canonical `content/` source.

Acceptance authorizes the resource model as a supported architectural option. It does **not** require repository-wide migration.

### Migration policy

Migration remains evidence-driven and should be proposed per framework. Prefer migration only when a framework has enough mixed concerns, examples, or orchestration material that the separation materially improves maintainability or progressive disclosure. Simple, coherent single-file frameworks remain valid.

A migration must preserve:

- the single shipped root `SKILL.md` entrypoint;
- canonical ownership in `content/` when layered;
- no duplication between `content/`, `examples/`, and `prompt/`;
- existing runtime registry and detector contracts;
- shipped-link and extracted-artifact integrity;
- global SoulMap doctrine and safety ownership.
