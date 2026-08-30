# Competitive intelligence and controlled evolution audit

**Audit date:** 2026-08-30. **Purpose:** a requested benchmark of SoulMap against
other personal-AI, AI-knowledge, AI-agent, and AI-memory systems, to find
SoulMap-native improvements without changing what SoulMap is. This document
records the research and the reasoning, not just the conclusion, so a future
maintainer can see why an idea was accepted or rejected rather than only that it
was.

## Executive summary

SoulMap's strongest competitive position is not a missing feature. It is the set
of things every other researched category treats as the point of the product,
and SoulMap deliberately does not do: persistent cross-session memory, an
ingestible open-ended knowledge corpus, and autonomous tool-using agent
behavior. That refusal is documented doctrine (`SOULMAP.md` Rule 1,
`docs/engineering/known-limitations.md`, `docs/engineering/maintenance-boundary.md`),
not an oversight this audit discovered. External research in this pass, primary
sources throughout, confirms the categories SoulMap is closest to
(memory-as-a-service, RAG knowledge bases, MCP-style agent tooling) are built
around exactly that architecture, and confirms it is genuinely hard: even Mem0,
the leading managed memory layer, is documented as lacking a temporal model for
superseded facts, the same problem a memory layer would create for SoulMap.

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
* **Memory model:** none, by design. No cross-session memory bonding
  (`src/soulmap/runtime/memory/__init__.py`: "exists for bounded experiments
  only and is not part of the core product promise"). Every session starts
  fresh.
* **Agent model:** not an agent in the tool-calling sense. `framework_selector.py`
  is a deterministic dispatcher over ~27 named outcomes; it does not plan, does
  not call external tools, and does not decide its own next action.
* **Architecture invariant:** Library (`src/soulmap/runtime/{knowledge,guards,routing,io,config}/`)
  is the stable substrate; Framework (`skills/frameworks/<name>.md` plus
  `<name>_detector.py`) is the swappable unit. A new capability is either a new
  Framework pair or it does not belong in the runtime.
* **Non-goals, explicit and current:** no web app, no public API service, no
  database layer, no auth/account system, no background jobs, no additional
  platform adapters beyond the current four, no new framework not required by
  current doctrine (`maintenance-boundary.md`).

## External research (primary sources)

Selected for relevance to SoulMap's actual architecture, not for name
recognition. Marketing claims were not treated as technical evidence; every
claim below traces to official documentation, an official blog, or an
arxiv preprint.

| Project | Category | Primary source | What it actually does |
| --- | --- | --- | --- |
| Claude Agent Skills | Skill/capability system | [Agent Skills overview, Claude Platform Docs](https://platform.Claude.com/docs/en/agents-and-tools/agent-skills/overview) | Three-level progressive disclosure: name and description always loaded, full SKILL.md body loaded on activation, referenced files loaded only when needed |
| Mem0 | AI memory layer | [Mem0, "AI Agent Memory: The Complete Guide"](https://mem0.ai/blog/memory-in-agents-what-why-and-how); [Vectorize, "Best AI Agent Memory Systems in 2026"](https://vectorize.io/articles/best-ai-agent-memory-systems) | Dual-store (vector database plus knowledge graph) extraction pipeline that converts conversation turns into atomic memory facts; documented as lacking a temporal model, memories are stored and retrieved, not modeled as time-bounded facts that can be superseded |
| Letta (MemGPT) | AI memory / stateful agent framework | [Letta, "Agent Memory: How to Build Agents That Learn and Remember"](https://www.letta.com/blog/agent-memory/) | Tiered memory: core memory (editable, pinned to context), recall memory (searchable history), archival memory (vector-indexed cold storage); agent manages its own memory through explicit tool calls, an "LLM as operating system" model |
| AnythingLLM / Open WebUI | AI knowledge base / RAG workspace | [nullzen.dev, "AnythingLLM + RAG"](https://www.nullzen.dev/blog/anythingllm-rag-guide/); [aicoolies, "Open WebUI vs AnythingLLM"](https://aicoolies.com/comparisons/open-webui-vs-anythingllm) | Full-stack RAG: document ingestion, vector storage, per-workspace embedded corpus, multi-user access, agent and tool support |
| Second Me / Cheshire Cat AI / Second Brain Link | Personal digital twin / second brain | [Sider, "10 Best AI Second Me Tutorials"](https://sider.ai/blog/ai-tools/best-ai-second-me-tutorials-to-build-your-digital-twin-in-2025); [Second Brain Link](https://secondbrainlink.com/) | Hierarchical memory modeling trained or indexed from a user's own exported data, evolving as the user's behavior changes |
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
| Temporal / contradiction-aware memory | N/A, no memory to contradict | Acknowledged gap even in Mem0 | N/A | N/A | Not a SoulMap gap; a hard, industry-wide open problem |
| Response safety contract enforced independently of routing | Core capability (`response_safety_gate.py`, ADR 0001) | Not typically separated | Not typically separated | N/A | Genuine SoulMap strength, not commonly matched |
| Evaluation suite tied to source content | Core capability (238-item `eval-groups`, source-marker checks) | Not publicly documented at this granularity | Not typically documented | N/A | Genuine SoulMap strength |
| Multi-user / workspace isolation | N/A, single-user local knowledge base | N/A | Core capability | N/A | Out of scope; SoulMap has no account system by design |

## What competitors do better

* **Mem0 and Letta** solve real, hard problems in making an agent's
  personalization state durable and queryable across sessions. Their tiered
  and graph-based memory designs are more sophisticated than anything a
  memory-free product needs to build.
* **AnythingLLM and Open WebUI** solve open-ended document ingestion at scale
  (up to roughly 100,000 documents per one 2026 reference architecture), which
  a fixed, curated, ~90-file Markdown corpus never needs to.
* **MCP** solves tool fragmentation for agents that call multiple external
  services. SoulMap calls no external service and has no tools to fragment.

## What SoulMap already does better

* A response safety gate that independently re-derives crisis and dependency
  status after framework selection (ADR 0001), rather than trusting a single
  upstream classification, is a defense-in-depth pattern none of the
  researched projects document at this level of rigor for their own safety
  paths.
* A deterministic, source-marker-verified eval suite (`eval-groups`,
  238 items, 51 source-marker checks) ties every claimed routing outcome back
  to the specific Markdown line that justifies it. RAG-oriented systems
  typically evaluate retrieval quality (did the right chunk surface), not
  whether the system's claim about the user's stated concern is literally
  backed by a cited source, which is a stronger and more specific guarantee.
* An explicit, enforced anti-dependency response contract (every response
  must leave the user less dependent, not more) has no equivalent requirement
  in any of the researched categories. Personalization and memory products are
  , structurally, optimized for the opposite: more relevant recall over time
  increases perceived value and retention.

## SoulMap capability gaps

Applying Phase 10's classification to every candidate this audit considered:

| Candidate | Classification | Reasoning |
| --- | --- | --- |
| Persistent memory (any form) | INTENTIONALLY ABSENT | Directly conflicts with Rule 1 (anti-dependency) and the documented no-memory-bonding boundary |
| Open-corpus RAG retrieval | INTENTIONALLY ABSENT | Would replace curated, safety-reviewed knowledge with probabilistic retrieval over arbitrary content, undermining the safety-review guarantee the whole knowledge base depends on |
| Autonomous tool use / agent planning | INTENTIONALLY ABSENT | `maintenance-boundary.md` explicitly rejects background jobs, infra-heavy deployment logic, and scope beyond the current Claude-first flow |
| Temporal/contradiction modeling for memory | NOT APPLICABLE | There is no memory to model contradictions in |
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
profile. This is a deliberately different, narrower kind of personalization
than any researched competitor implements, and it is consistent with the
product's anti-dependency stance. No gap found.

## Skill and agent audit

Cross-checked against Anthropic's own documented Agent Skills model
([overview](https://platform.Claude.com/docs/en/agents-and-tools/agent-skills/overview)):

* **Level 1 (name and description always loaded):** every `skills/*/SKILL.md`
  and every `.claude/skills/*/SKILL.md` already has YAML front matter with
  `name` and `description`. Confirmed already correct.
* **Level 2 (full body on activation):** `skills/*/SKILL.md`'s own workflow
  sections already point to specific files to read next rather than inlining
  everything. Confirmed already correct.
* **Level 3 (referenced files on demand):** the Framework-pair pattern
  (`docs/engineering/library-vs-framework.md`) already treats each
  `skills/frameworks/<name>.md` as a file loaded only when its detector fires.
  Confirmed already correct.

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
SoulMap more should not become the goal. Every researched competitor's
differentiation instead comes from data (what it knows about you) or
capability breadth (what it can do for you). SoulMap's differentiation is
architectural restraint applied consistently to a narrow, safety-reviewed
domain. That is a coherent, defensible identity and this audit found no
evidence it is weak or accidental.

## Python and documentation changes made

| File | Change | Reason |
| --- | --- | --- |
| `docs/engineering/library-vs-framework.md` | Added one paragraph naming the existing Skill loading behavior as progressive disclosure and citing Anthropic's own Agent Skills documentation | The behavior already existed and was already correct; only the cross-reference to the now-standard industry term was missing, and a future maintainer benefits from knowing the pattern has a name and prior art |

No Python changes. No new Skills. No existing Skill modified. No dependency
added.

## Required final decision

### KEEP

* No persistent memory, no cross-session bonding, single-user, local
  knowledge base with no backend.
* Deterministic, auditable routing (`framework_selector.py`) over probabilistic
  retrieval.
* The Library-vs-Framework boundary and the one-file-pair-per-framework
  discipline.
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

* Persistent or long-term memory in any form, including "lightweight"
  preference caching.
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
