# Competitive intelligence and controlled evolution audit

**Audit date:** 2026-08-30. **Purpose:** a requested benchmark of SoulMap against
other personal-AI, AI-knowledge, AI-agent, and AI-memory systems, to find
SoulMap-native improvements without changing what SoulMap is. This document
records the research and the reasoning, not just the conclusion, so a future
maintainer can see why an idea was accepted or rejected rather than only that it
was.

## Historical scope

> This report is a research snapshot dated 2026-08-30. Its architecture descriptions and
> non-goals record the repository as understood during that audit; they are not current
> implementation or routing instructions. For the current ownership and route model, see
> [the repository contract](../engineering/repo-contract.md),
> [the Library/framework boundary](../engineering/library-vs-framework.md), and
> [the November 2026 runtime ownership follow-up](skills-runtime-ownership-followup-2026-11.md).

## Executive summary

SoulMap's strongest competitive position is not a missing feature. It is the set
of capabilities many products in the reviewed categories emphasize, while SoulMap
deliberately keeps a narrower scope: a SoulMap-owned persistent conversation store,
open-corpus retrieval, and autonomous tool-using agent behavior are not part of the
product. That boundary is documented in the repository's doctrine and maintenance
contract, not inferred from competitor marketing. The comparison below uses a mix of
first-party documentation and secondary analysis; it is not a hands-on benchmark or an
exhaustive survey. The sources illustrate different product categories, but do not
establish that every competitor follows the same model or that temporal memory is an
industry-wide unsolved problem.

One implementation-worthy finding did surface, and it is small: SoulMap's Skill
layer already matches Anthropic's own documented progressive-disclosure model
for Agent Skills (front matter name and description loaded first, full body
loaded on activation, referenced files loaded only when needed) but nothing in
the repository names that pattern explicitly or cites the alignment. That is a
documentation clarity gap, not a capability gap, and is the one change this
audit made.

## SoulMap identity and invariants (derived from the repository)

Already established doctrine, not re-derived here at length. Summarized from
`SOULMAP.md`, `docs/engineering/repo-contract.md`,
`docs/engineering/maintenance-boundary.md`, and
`docs/engineering/library-vs-framework.md`:

* **Purpose:** a reflective companion that helps a user hear themselves more
  clearly, whose response contract requires every reply to leave the user less
  dependent, not more.
* **Knowledge model:** a small, hand-authored, safety-reviewed Markdown corpus
  under `skills/`, functioning as deterministic routing targets for a
  rule-based Python selector, not an embedded corpus for open-ended retrieval.
* **SoulMap-controlled memory:** no persistent conversation database or memory
  service is provided by this repository. A host platform may still surface prior-session
  context or memory; that data is outside SoulMap's storage and retention control. The
  continuity contract in `skills/meta/session-continuity.md` permits only the context
  actually supplied by the platform and forbids treating fragments as a full session.
  The former experimental SoulMap-owned memory layer was removed because it was not part
  of the core product promise.
* **Agent model:** not an agent in the tool-calling sense. `framework_selector.py`
  is a deterministic dispatcher over ~27 named outcomes; it does not plan, does
  not call external tools, and does not decide its own next action.
* **Architecture model recorded at this audit date:** Library
  (`src/soulmap/runtime/{knowledge,guards,routing,io,config}/`) was treated as the
  stable substrate, while a primary Framework was described as a Markdown source plus
  a detector. That simplified pair model is historical, not a current one-to-one rule:
  current repository guidance distinguishes primary routed frameworks from supporting
  lenses and secondary-layer knowledge.
* **Non-goals recorded at the audit date (2026-08-30):** no web app, no public API service, no
  database layer, no auth/account system, no background jobs, no additional
  platform adapters beyond the current four, no new framework not required by
  current doctrine (`maintenance-boundary.md`).

## External research and source quality

Selected for relevance to SoulMap's actual architecture, not for name recognition.
The source set is mixed: first-party product documentation and vendor blogs are used
for claims about a vendor's own product; third-party tutorials and comparisons are
secondary analysis and are labeled as such. This is a desk-research snapshot, not a
hands-on benchmark, security audit, or exhaustive competitor survey. Marketing claims
are not treated as technical evidence.

| Project | Category | Sources and source type | What the reviewed sources describe |
| --- | --- | --- | --- |
| Claude Agent Skills | Skill/capability system | [Agent Skills overview, Claude Platform Docs](https://platform.Claude.com/docs/en/agents-and-tools/agent-skills/overview) | Three-level progressive disclosure: name and description always loaded, full SKILL.md body loaded on activation, referenced files loaded only when needed |
| Mem0 | AI memory layer | [Mem0 vendor blog](https://mem0.ai/blog/memory-in-agents-what-why-and-how) (first-party); [Vectorize comparison](https://vectorize.io/articles/best-ai-agent-memory-systems) (secondary) | The vendor blog describes its memory architecture and extraction approach. The Vectorize comparison characterizes temporal supersession as a gap; that is a third-party assessment, not a statement from Mem0, and this audit did not independently test the product. |
| Letta (MemGPT) | AI memory / stateful agent framework | [Letta, "Agent Memory: How to Build Agents That Learn and Remember"](https://www.letta.com/blog/agent-memory/) | Tiered memory: core memory (editable, pinned to context), recall memory (searchable history), archival memory (vector-indexed cold storage); agent manages its own memory through explicit tool calls, an "LLM as operating system" model |
| AnythingLLM / Open WebUI | AI knowledge base / RAG workspace | [nullzen.dev RAG guide](https://www.nullzen.dev/blog/anythingllm-rag-guide/) and [aicoolies comparison](https://aicoolies.com/comparisons/open-webui-vs-anythingllm) (third-party secondary sources) | These sources describe common RAG workspace capabilities such as document ingestion, vector storage, workspace collections, and tool support. They are not official product specifications; verify details against each project's current documentation before relying on them. |
| Second Me / Cheshire Cat AI / Second Brain Link | Personal digital twin / second brain | [Sider tutorial roundup](https://sider.ai/blog/ai-tools/best-ai-second-me-tutorials-to-build-your-digital-twin-in-2025) (secondary); [Second Brain Link](https://secondbrainlink.com/) (vendor site) | The secondary roundup describes personal-data indexing and evolving memory as common approaches in this category. Product-specific architecture claims require confirmation from each vendor's current documentation. |
| Model Context Protocol (MCP) | Agent tool-discovery protocol | [Model Context Protocol Blog, "2026-07-28 Specification"](https://blog.modelcontextprotocol.io/posts/2026-07-28/) | Client-server protocol for an AI application to discover and call external tools and data sources at runtime, moving toward a stateless core in the 2026-07-28 release candidate |

## Competitive capability matrix

Only categories where a genuine comparison is possible are included. A dash
means the category does not apply to SoulMap's actual product shape, not that
SoulMap scored zero.

| Capability | SoulMap | Mem0 / Letta | AnythingLLM / Open WebUI | Claude Agent Skills | Relevance to SoulMap |
| --- | --- | --- | --- | --- | --- |
| Persistent cross-session memory | Absent, by design | Core capability | Per-workspace conversation history | N/A | Conflicts with SoulMap's anti-dependency architecture |
| Open-corpus retrieval (RAG) | Absent, by design | N/A | Core capability | N/A | Would replace curated, safety-reviewed routing with probabilistic retrieval |
| Deterministic, auditable routing | Core capability (`framework_selector.py`) | N/A | N/A | N/A | SoulMap's actual differentiator |
| Skill progressive disclosure | Matches the documented pattern | N/A | N/A | Documented origin of the pattern | Already aligned, undocumented as such |
| Autonomous tool use / planning | Absent, by design | Partial (Letta) | Partial | Depends on host | Would make SoulMap agent-centric, against `maintenance-boundary.md` |
| Temporal / contradiction-aware memory | N/A, no SoulMap-owned store to reconcile | A third-party comparison identifies a limitation in one Mem0 architecture | N/A | N/A | Not a SoulMap requirement; this desk review does not establish an industry-wide gap |
| Response safety contract enforced independently of routing | Core capability (`response_safety_gate.py`, ADR 0001) | Not typically separated | Not typically separated | N/A | Genuine SoulMap strength, not commonly matched |
| Evaluation suite tied to source content | Core capability (238-item `eval-groups`, source-marker checks) | Not publicly documented at this granularity | Not typically documented | N/A | Genuine SoulMap strength |
| Multi-user / workspace isolation | N/A, single-user local knowledge base | N/A | Core capability | N/A | Out of scope; SoulMap has no account system by design |

## What competitors do better

* **Mem0 and Letta** address durable, queryable agent state across sessions. Their
  memory architectures solve a different problem from SoulMap's curated reflective
  knowledge layer; this audit does not compare their quality or reliability.
* **AnythingLLM and Open WebUI** address open-ended document ingestion and RAG
  workflows. SoulMap's curated Markdown knowledge base has a different scope and
  does not need to reproduce a general-purpose document-ingestion workspace.
* **MCP** standardizes tool discovery and invocation for applications that use external
  tools. The core SoulMap runtime does not call external tools; repository maintenance
  and explicitly selected network operations are separate concerns.

## What SoulMap already does better

* The repository documents a response safety gate that independently re-derives
  crisis and dependency status after framework selection (ADR 0001). This is a
  concrete defense-in-depth design in SoulMap. The sources reviewed here do not
  provide enough comparable implementation detail to claim that other products
  lack equivalent mechanisms.
* At the audit date, the deterministic, source-marker-verified eval suite
  (`eval-groups`, 238 items, 51 source-marker checks) tied routing outcomes to
  specific Markdown source lines. This is a different evaluation target from
  retrieval-hit-rate metrics. It is not a comparative claim that RAG systems
  cannot provide source-grounded answers or stronger guarantees.
* SoulMap's doctrine states an anti-dependency response goal: interactions should
  return agency to the user rather than encourage reliance on the system. The
  reviewed product sources do not establish whether other products have an
  equivalent requirement. Do not infer the absence of safeguards from silence
  in public documentation, or generalize one business model to every product.

## SoulMap capability gaps

Applying Phase 10's classification to every candidate this audit considered:

| Candidate | Classification | Reasoning |
| --- | --- | --- |
| SoulMap-controlled persistent memory service | INTENTIONALLY ABSENT | The project does not own a cross-session store; host-platform memory/context remains outside its control and is handled by the session-continuity protocol |
| Open-corpus RAG retrieval | INTENTIONALLY ABSENT | Would replace curated, safety-reviewed knowledge with probabilistic retrieval over arbitrary content, undermining the safety-review guarantee the whole knowledge base depends on |
| Autonomous tool use / agent planning | INTENTIONALLY ABSENT | `maintenance-boundary.md` explicitly rejects background jobs, infra-heavy deployment logic, and scope beyond the current Claude-first flow |
| Temporal/contradiction modeling for a SoulMap-owned memory store | NOT APPLICABLE | The repository does not maintain a persistent memory store; any host-provided context is not stored or reconciled by SoulMap |
| MCP-style tool discovery | NOT APPLICABLE | SoulMap has no external tools to discover |
| Multi-user workspace isolation | NOT APPLICABLE | No account system by design |
| Naming the existing Skill structure's alignment with progressive disclosure | MISSING BUT NOT NEEDED AS CODE, WORTH ONE DOC NOTE | The behavior already exists and is already correct; only the cross-reference was missing |

No candidate reached MISSING AND SHOULD ADD.

## False gaps: capabilities this audit explicitly rejected

| Idea | Why competitors use it | Why it does not fit SoulMap | Risk of adopting it | Decision |
| --- | --- | --- | --- | --- |
| Persistent user-preference memory | Increases personalization and retention | SoulMap's core safety rule is that responses must reduce dependency over time; a system that remembers and adapts to keep a user engaged is the exact mirror-trap pattern `skills/brand/competitive-differentiation.md` positions against | Would quietly convert SoulMap from anti-dependency to engagement-optimized, the single most important thing not to become | REJECT |
| Vector-embedded RAG over `skills/` | Scales to large, growing corpora; handles fuzzy queries | The corpus is small (~90 files) and deterministic routing already resolves every case the eval suite covers; RAG would replace a fully auditable "why did this framework activate" answer with a similarity score | Loses the safety-review guarantee: a retrieved chunk has not been checked against the same doctrine gate a hand-wired detector has | REJECT |
| MCP server/tool integration | Lets an agent call external services on demand | SoulMap has no external services to call and no product need for one; adding MCP scaffolding with nothing behind it is pure surface area | New dependency, new attack surface, no capability gained | REJECT |
| A "digital twin" trained on the user's own data | Personalizes deeply to one person's history | SoulMap's founder-numerology precedent already establishes the opposite discipline for personal data (numbers only, no identifiers); training a model on personal history is a different order of data retention entirely | Directly conflicts with the existing `docs/operations/PRIVACY.md` no-backend, no-storage position | REJECT |
| Periodic AI-identity reminders (California SB 243 style) | Regulatory compliance for products likely used by minors | Already tracked as a real, open, but out-of-scope gap in `docs/operations/REGULATORY.md`'s own "Gap: Timed AI Reminders" section; this audit found nothing new to add to that existing, honest accounting | None from not touching it; it is already correctly recorded as open | DEFER (already tracked, not re-opened here) |

## Memory, provenance, and temporal knowledge audit

Phases 14 to 17 of the source prompt ask whether SoulMap models memory,
provenance, and time-varying facts well. The honest answer, evidenced above,
is that these questions do not apply: SoulMap has no memory store, so there is
nothing to model provenance or supersession for. The one place SoulMap does
handle a provenance-adjacent problem is symbolic reports a user brings into a
conversation (`skills/spiritual/symbolic-report-handling.md`,
`skills/spiritual/numerology-chakra-policy.md`), and that handling already
follows the right discipline for its scope: treat the report as the user's own
material, reflect it symbolically, never store it, never confirm it as fact.
No gap found here.

## Personalization audit

SoulMap's personalization is structural, not data-driven: stage classification
(`skills/meta/stage-classifier.md`) adjusts response depth within a single
session based on where the conversation already is, not on a persisted user
profile. This was the documented approach at the audit date. In November 2026, the
continuity contract was clarified to permit only relevant prior-session context
explicitly supplied by the host in the current prompt; SoulMap still does not
independently store or retrieve user history. This is a narrower form of
contextual adaptation than a SoulMap-owned profile or memory store. The audit
did not compare every competitor's personalization behavior.

## Skill and agent audit

Cross-checked against Anthropic's own documented Agent Skills model
([overview](https://platform.Claude.com/docs/en/agents-and-tools/agent-skills/overview)):

* **Level 1 (name and description always loaded):** the shipped root `SKILL.md`
  and internal `.claude/skills/*/SKILL.md` files use YAML front matter with
  `name` and `description`.
* **Level 2 (full body on activation):** the shipped root `SKILL.md`'s workflow
  sections already point to specific files to read next rather than inlining
  everything. Confirmed already correct.
* **Level 3 (referenced files on demand):** the primary-framework pattern
  described at the audit date treated each routed knowledge source as a file loaded
  when its route activated. Current file roles are more explicit: primary routes,
  secondary layers, and supporting lenses are not interchangeable. See
  `docs/engineering/library-vs-framework.md` for the current rule. This research
  snapshot is not the route registry.

SoulMap's Skill layer already implements the pattern this research names.
Nothing in the repository states that alignment explicitly, which is the one
documentation gap this audit is acting on.

Composability, discoverability, and scoping were also checked directly
against `.claude/skills/README.md`'s index (22 skills, exact match to the
directories on disk, confirmed in Phase 19's forensic audit earlier this
session) and found already correct: no overlapping skills, no duplicated
scope, one clear "Do not use this skill for" pointer per skill file.

## Evaluation audit

`eval-groups` (238 items, 666 assertion checks, 252 source checks, 51 source-marker
checks), `eval-responses`, `eval-markdown-contracts`, and the safety eval
regression suite (79 cases) already cover routing correctness, response
structure, doctrine-to-Markdown sync, and safety-category coverage. This is
more granular than the retrieval-hit-rate evaluation typical of the RAG
systems researched, because SoulMap's routing is deterministic and therefore
checkable exactly, not just approximately. No gap found.

## Personal AI vs. generic AI audit

What makes SoulMap genuinely personal is not stored data about the person. It
is a fixed, curated set of reflective lenses applied to whatever the person
brings to a single conversation, with a hard structural requirement that using
SoulMap more should not become the goal. Within this limited comparison set, the products reviewed emphasize persistent
context, document retrieval, or broader tool capability. That does not establish
that every competitor differentiates in the same way. SoulMap's intended
differentiation is architectural restraint applied to a narrow, safety-reviewed
domain; whether that position is commercially defensible requires separate
market and user research.

## Python and documentation changes made

| File | Change | Reason |
| --- | --- | --- |
| `docs/engineering/library-vs-framework.md` | Added one paragraph naming the existing Skill loading behavior as progressive disclosure and citing Anthropic's own Agent Skills documentation | The behavior already existed and was already correct; only the cross-reference to the now-standard industry term was missing, and a future maintainer benefits from knowing the pattern has a name and prior art |

No Python changes. No new Skills. No existing Skill modified. No dependency
added.

## Required final decision

### KEEP

* No SoulMap-controlled persistent memory store or cross-session memory bonding. Host
  platforms may surface prior context under their own memory and privacy controls.
  The knowledge base remains local to the host's use of the shipped artifact; there is
  no SoulMap-operated backend.
* Deterministic, auditable routing (`framework_selector.py`) over probabilistic
  retrieval.
* The primary-route versus supporting-lens boundary; do not impose a one-file-pair rule
  on every knowledge file.
* The independent, defense-in-depth safety gate re-derivation (ADR 0001).
* The source-marker-verified eval suite as the standard for adding any new
  routing behavior.
* The anti-dependency response contract as a non-negotiable rule, not a
  configurable preference.

### IMPROVE

* Documentation clarity connecting SoulMap's already-correct Skill loading
  behavior to the now-standard "progressive disclosure" term, so a new
  contributor coming from the broader Claude Skills ecosystem recognizes the
  pattern immediately. Done in this pass.

### DO NOT ADD

* A SoulMap-controlled persistent or long-term memory store, including "lightweight"
  preference caching. Host-platform memory remains outside this repository's control.
* Vector-embedded retrieval over `skills/` or any other corpus.
* MCP server or client integration, or any external tool-calling capability.
* Multi-user accounts, workspaces, or authentication.
* A "digital twin" or personal-data-trained model of the user.
* Autonomous planning or self-directed multi-step task execution.

## Validation basis

This audit made one documentation change. Validated with
`uv run soulmap markdown-contract --root .`,
`uv run soulmap check-links --root .`, `uv run soulmap check-case --root .`,
and `uv run soulmap lint`. No Python, Skill, test, or packaging surface was
touched, so no additional gate applies beyond those and the standard
pre-push checklist.
