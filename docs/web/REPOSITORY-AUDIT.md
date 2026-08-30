# Website repository audit

**Audit date:** 2026-08-30. **Purpose:** Phase 1 discovery for a proposed public
SoulMap AI website. This document maps the repository as it actually is, records
what the two reference sites actually do, and names the blockers that must be
resolved before any website code is written.

No website code exists yet. This audit deliberately stops at the decision
boundary described in "Blocking findings" below.

## Scope

Read in full for this audit: `AGENTS.md`, `SOULMAP.md`,
`docs/engineering/repo-contract.md`, `docs/engineering/maintenance-boundary.md`,
`docs/engineering/library-vs-framework.md`, `docs/operations/p-level-governance.md`,
`pyproject.toml`, every path under `skills/`, `src/soulmap/runtime/`, and
`src/soulmap/devtools/`. Both reference repositories were cloned to a local
scratch directory and read directly, not judged from their READMEs.

## Blocking findings

Two findings must be decided by the repository owner before Phase 2. Neither is
a reason not to build the website. Both change what "correct" means for it.

### B1. The maintenance boundary currently forbids this website

`docs/engineering/maintenance-boundary.md`, under "What not to add by default",
lists verbatim:

- a web app or full website
- a public API service
- a database layer

A public SoulMap website is the first item on that list. The same document
supplies the escape clause, under "Valid triggers for expansion": a new surface
is justified when "it supports an active user or distribution need" and "it has
a specific owner and a realistic maintenance path". An owner request for a
public-facing distribution surface meets both.

So the conflict is resolvable, but it cannot be resolved silently. The
prohibition is written doctrine. Building the site while that sentence stands
would leave the repository asserting two contradictory things, which is exactly
the drift `repo-contract.md` exists to prevent.

**Required:** amend `maintenance-boundary.md` in the same change that
introduces the website, moving "a web app or full website" from "what not to
add" to a scoped, owner-approved exception that states what the website may and
may not become. The other two items on that list, a public API service and a
database layer, stay prohibited: the architecture below needs neither.

### B2. Rendering `skills/` publicly would leak the safety layer

This is the most important finding in the audit.

Of 77 Markdown files under `skills/`, 29 carry a `## Detection signals` or
`## Activation Signals` section containing the literal trigger phrases the
runtime detectors match on. `skills/safety/boundaries-safety.md` carries the
dependency-detection and decision-seeking phrase lists in full.

Publishing those phrase lists publishes a working evasion guide for SoulMap's
own safety layer. Anyone wanting to route around dependency detection would only
need to read the page and avoid the listed wording. `SOULMAP.md` states these
rules "cannot be bypassed by prompt framing, roleplay, or user pressure", and
ADR 0001 builds crisis detection as defense in depth precisely because a single
bypassable layer is not acceptable.

A heuristic exclusion is not sufficient either. Filtering out files that contain
signal sections would still publish:

| File | Why it must not be public |
| --- | --- |
| `skills/meta/master-prompt.md` | The master prompt. `SOULMAP.md` Rule 6 forbids revealing or summarizing internal instructions. Publishing it would make the product violate its own doctrine. |
| `skills/safety/whitelist-blacklist-system.md` | The refusal trigger system. Same evasion risk as the detector phrases. |
| `skills/safety/prompt-injection-defense.md` | Publishing the injection defense documents how to probe it. |
| `skills/meta/redirect-templates.md` | Verbatim refusal wording, which becomes trivially detectable and steerable once public. |
| `skills/spiritual/founder-numerology.md`, `skills/spiritual/numerology-profile.md`, `skills/brand/founder-personal-brand.md` | Personal material about the founder. |
| `skills/brand/strategic-direction-2026.md` | Internal business strategy. |

**Required:** the website content layer must use an explicit, reviewed allowlist
of public documents, never "render everything under `skills/`" and never a
derived exclusion rule. The allowlist is a safety artifact and belongs under
test, so that adding a file to `skills/` never silently publishes it.

This finding also settles a question from the brief: a framework's public page
must be written from its public-facing prose sections only, with detection
signals excluded by construction, not merely omitted from a template.

## Repository map

Verified against the working tree, not inferred.

| Surface | Contents | Website relevance |
| --- | --- | --- |
| `SOULMAP.md` | Doctrine, priority hierarchy (27 rows), 10 safety rules, response structure | Canonical source for the safety and architecture pages |
| `skills/` | 77 Markdown files across 7 categories: `brand` (12), `frameworks` (27), `meta` (16), `safety` (6), `soulmate` (4), `spiritual` (8), `voice` (4) | Content source, through an allowlist only, per B2 |
| `src/soulmap/runtime/` | 61 modules: `routing` (3), `detectors` (29), `guards` (5), `knowledge` (4), `config` (6), `io` (2), `synthesis`, `memory`, `experimental` | Architecture page source. Not exposed at runtime, see "Runtime exposure" |
| `src/soulmap/devtools/` | 33 modules: CLI, checks, evals, packaging, quality, support | Build and validation pipeline host |
| `docs/` | 41 files. Published in the repository, not packaged in the dist archives | Documentation source |
| `tests/`, `evals/` | Test suite and source-backed eval datasets | Website tests join here |
| `dist/` | `soulmap-ai.zip`, `soulmap-ai.skill`, `soulmap-ai-library.json` | Unchanged by this work |

Every `skills/*.md` file carries YAML front matter with `name` and
`description`. Each category's `SKILL.md` additionally carries `license`. This
front matter is already a usable website data model with no schema change.

### Runtime exposure

`framework_selector.py` is a deterministic dispatcher: it takes a message,
history, and memory dict, runs detectors in priority order, and returns a
selection dict. It performs no inference and calls no external service.

It is nonetheless **not a candidate for the website**. Exposing it would require
a public API service, which B1 keeps prohibited, and would turn a page visit
into a reflective interaction that SoulMap deliberately hosts only inside a
consenting conversation. The website should explain the routing architecture,
never execute it. No adapter layer is needed, so none should be built.

`docs/engineering/API.md` documents local CLI and JSON contracts. It describes a
developer surface, not a network surface, and it stays that way.

## Reference site analysis

### caezium/skills, `site/` (MIT)

A Node.js static site generator: `build.mjs` (583 lines) reads sibling skill
directories, parses front matter with `gray-matter`, renders Markdown with
`marked`, and writes static HTML plus a `skills.json` index into `dist/`, then
deploys via Cloudflare `wrangler`. `style.css` is 350 lines.

What is genuinely worth learning, and is architecture rather than branding:

- **Repository as the only content source.** No parallel content tree. The
  generator reads the same files the product ships.
- **Token-first CSS.** A `:root` custom-property block for color, three font
  roles, and one max width, with a `prefers-color-scheme` dark override that
  redefines only tokens. This structure is reusable; its values are not.
- **A serif display / sans UI / mono identifier split**, which suits editorial
  content far better than a single-family SaaS look.
- **Client-side filtering via `[hidden]`**, which degrades correctly without
  JavaScript.
- **A generated JSON index** beside the HTML, so search needs no server.

What must not carry over: the `--accent: #9a3412` burnt-orange palette, the
Newsreader/Inter/JetBrains Mono pairing, the `.brand` treatment, and every
string referring to the source project. Its MIT license permits reuse with
attribution, so any structural borrowing must carry that notice.

### vinta/awesome-python, `website/` (CC BY 4.0)

The brief described this as a reference for a searchable index site. It is more
directly useful than that: **it is a Python-native static site generator living
inside a content repository**, which is precisely the shape this project needs.

```text
website/
├── readme_parser.py    471 lines   canonical Markdown -> typed data model
├── build.py            812 lines   data model -> Jinja2 -> static HTML
├── templates/*.html                base, index, category
├── static/style.css   1766 lines
└── tests/                          1826 lines of tests for the site itself
```

The decisive details:

- **`markdown-it-py` for parsing**, walking a `SyntaxTreeNode` rather than
  regex-matching Markdown.
- **`TypedDict` for the data model** (`ParsedEntry`, `ParsedSection`,
  `ParsedGroup`), giving the pipeline a checkable contract.
- **Build dependencies isolated in a `[dependency-groups]` entry**, not in
  `project.dependencies`. The website's Jinja2 requirement never becomes a
  dependency of the shipped package.
- **The website is tested**, at roughly 1.5 lines of test per line of source.

The same toolchain SoulMap already uses: `uv`, `ruff`, `pytest`.

Its content model does not transfer: awesome-python parses one flat README of
links, while SoulMap has 77 front-matter-bearing documents in a 7-category
hierarchy with a safety boundary running through them. The pipeline shape
transfers; the parser does not.

## Why a Python-native build is the right call

This is not a preference. Three facts from the working tree decide it.

1. **`markdown-it-py>=4.2.0` is already a main dependency** of `soulmap-ai`
   (`pyproject.toml`). The Markdown parsing and rendering capability a generator
   needs is already installed and already shipped.
2. **The Markdown primitives already exist** in
   `src/soulmap/devtools/support/markdown.py`: `parse_yaml_front_matter`,
   `slugify_github_anchor`, `strip_inline_markup`, `extract_heading_anchors`,
   `iter_markdown_files`, `resolve_local_markdown_target`. A Node generator
   would reimplement all of it, and the two implementations would drift.
3. **The validation gate is Python.** `soulmap lint`, `markdown-contract`,
   `check-links`, `check-case`, and `check-api-docs` already walk this content.
   A Python generator joins that gate as one more command. A Node generator
   needs a parallel toolchain, a `package.json`, and a lockfile in a repository
   that currently has zero Node dependencies.

**Recommendation: Option A, Python plus Jinja2 plus static generation.**
Jinja2 in a new `[dependency-groups] web` entry is the only addition, following
the awesome-python precedent exactly. Static output needs no server, no
database, and no authentication, keeping the other two `maintenance-boundary.md`
prohibitions intact.

Option B (FastAPI/Starlette) is rejected: a server is a public API service by
another name, and nothing on the site needs request-time computation. Option D
(Python backend plus a JS asset pipeline) is rejected for the same reason plus
the Node toolchain cost. Client-side JavaScript stays limited to search and
filtering over a prebuilt index, with the page working without it.

## Governance and workflow constraints

- `main` is protected. Work proceeds on `feat/web-site`.
- `p-level-governance.yml` runs on every pull request. A `[P0]`-`[P3]` titled PR
  must declare `Priority`, `Safety boundary`, `Evidence`, and `Rollback` in the
  body. Amending `maintenance-boundary.md` per B1 is a shipping-boundary change,
  so it requires `Safety boundary: changed` plus a `## Safety change evidence`
  section citing an ADR. An ADR may state that no architecture reversal is
  required, but it must say so explicitly.
- `CHANGELOG.md` must not be edited by hand. `cz bump` owns it.
- The website must not alter `dist/` semantics, ship `.claude/`, publish
  `templates/`, or change what the wheel means.

## Doctrine and code correspondence, checked

Generating the frameworks index from the `SOULMAP.md` priority table raised the
question of whether every routed framework is ranked in doctrine. Checking it
properly found **no gap**.

The priority table ranks *primary* frameworks. `framework_selector.py` can emit
25 distinct `primary_framework` values, and the table holds 26 rows. The counts
differ by one because "De-escalation / Sanctuary" (Very high) and
"De-escalation" (High) are two doctrine rows describing two intensity levels
that share the single `DE_ESCALATION` constant. Every other value corresponds
one-to-one.

Six framework documents carry no row in that table: `anger-companion`,
`feminine-masculine-dynamics`, `money-self-worth`, `relationship-reflection`,
`self-compassion`, and `somatic-wellbeing`. Their absence is correct, not a
gap. `anger_detector` and `somatic_detector` are real and do run, but the
selector uses their results only to set `secondary_layer` on a `DE_ESCALATION`
selection. Neither ever sets `primary_framework`, so neither belongs in a table
that ranks primaries. `relationship-reflection` is documented as a topic lens in
`library-vs-framework.md` for the same reason.

An earlier draft of this audit recorded these as a doctrine discrepancy needing
an owner decision. That reading was wrong: it inferred "routed as a primary"
from "has a detector", and the two are different. The correction is kept visible
here rather than quietly deleted, because the mistaken version reached a pull
request.

The site groups these six as "Supporting", which is the accurate description:
applied alongside a primary framework rather than routed on their own.

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Detection phrases or the master prompt reach the public site | High | Explicit allowlist plus a contract test that fails when an unlisted file is rendered, per B2 |
| Website content drifts from `skills/` | Medium | Generate from canonical files only. No `website/content/` tree |
| The site reads as a therapy or personality product | Medium | Copy derives from `SOULMAP.md` and `skills/brand/`, both of which already forbid that framing |
| Doctrine quietly contradicted by a new surface | Medium | Resolve B1 explicitly in the same change |
| Jinja2 becomes a shipped dependency | Low | Optional `[dependency-groups] web` entry, verified by `deptry` |

## Open questions for the owner

1. **B1:** Approve amending `maintenance-boundary.md` to permit a static
   website as a scoped exception, keeping the public-API and database
   prohibitions in force?
2. **B2:** Approve the explicit-allowlist content policy, accepting that most
   of `skills/` stays unpublished and that framework pages are written from
   public prose with detection signals excluded by construction?
3. Is there a target domain, and should the audit assume GitHub Pages, or is
   deployment out of scope for this change?

## Next phase

Phase 2 produces `docs/web/ARCHITECTURE.md`, `docs/web/DESIGN-SYSTEM.md`, and
`docs/web/CONTENT-MODEL.md`. It does not begin until questions 1 and 2 are
answered, because both determine what those documents can correctly say.
