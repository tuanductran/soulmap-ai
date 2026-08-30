# Website content model

**Status:** Phase 2 proposal, approved for implementation. **Date:** 2026-08-30.

This document defines exactly what reaches the public website and what cannot.
It is a safety artifact. Treat a change here the way the repository treats a
change to a detector: with evidence, a test, and a reviewer.

## The governing rule

Nothing is public unless it is named in the allowlist.

The generator refuses to render a document that is not explicitly listed. A file
added to `skills/` tomorrow is private by default and stays private until
someone lists it and a reviewer approves that line. The failure mode is a build
error, never a silent publication.

This inverts the usual static-site default, and it is inverted on purpose. The
audit found that a filter-based approach fails open: it would still have
published `skills/meta/master-prompt.md`, which `SOULMAP.md` Rule 6 forbids
revealing.

## Two layers of exclusion

An allowlisted file is still not published whole. Two internal section types are
removed by construction, before rendering, not merely omitted by a template.

| Section heading | Files | Why it is never public |
| --- | --- | --- |
| `Detection signals`, `Activation Signals` | 29 | The literal phrases the detectors match. Publishing them publishes a working evasion guide for the safety layer |
| `Paired template` | 26 | Internal composition wiring. It cross-references `skills/meta/redirect-templates.md`, `deep-inquiry-bank.md`, and `framework-template-map.md`, none of which are public, so rendering it would both expose the internal map and emit dead links |

Removal happens in `content.py` while walking the parsed document, so a template
author cannot reintroduce the content by accident and a new template cannot leak
it. The section text never enters the page model at all.

## The allowlist

Public. Every entry is a deliberate decision.

| Group | Files | Rationale |
| --- | --- | --- |
| Doctrine | `SOULMAP.md` | Already ships in every extracted package and is written to stand alone publicly |
| Frameworks | the 26 `skills/frameworks/*.md` content files (all except `SKILL.md`), minus their internal sections | This is the knowledge the site exists to explain |
| Brand, public subset | `brand-doctrine.md`, `brand-positioning.md`, `message-hierarchy.md`, `competitive-differentiation.md`, `research-backing.md` | Written for public positioning already |
| Voice | `persona-voice.md`, `session-rituals.md` | Explains tone and rhythm without exposing enforcement |

Deliberately excluded, with the reason recorded so a future maintainer does not
relitigate it from scratch:

| File or group | Reason |
| --- | --- |
| `skills/meta/master-prompt.md` | `SOULMAP.md` Rule 6 forbids revealing internal instructions. Publishing it would make the product violate its own doctrine |
| `skills/safety/boundaries-safety.md` | Carries the dependency-detection and decision-seeking phrase lists in full |
| `skills/safety/whitelist-blacklist-system.md` | The refusal trigger system |
| `skills/safety/prompt-injection-defense.md` | Publishing the defense documents how to probe it |
| `skills/meta/redirect-templates.md` | Verbatim refusal wording becomes steerable once public |
| `skills/meta/deep-inquiry-bank.md`, `framework-template-map.md`, `response-structure.md`, `stage-classifier.md`, `execution-pipeline.md`, `orchestration.md` | Internal response scaffolding. Knowing the exact structure makes replies predictable and gameable |
| `skills/spiritual/founder-numerology.md`, `numerology-profile.md`, `skills/brand/founder-personal-brand.md` | Personal material about the founder |
| `skills/brand/strategic-direction-2026.md` | Internal business strategy |
| `skills/spiritual/*` remainder, `skills/soulmate/*` | Symbolic and relational material that needs the surrounding conversational guardrails to be read safely. The site describes these categories rather than reproducing them |
| `templates/`, `.claude/`, `docs/`, `tests/`, `evals/`, `src/` | Not product knowledge. `docs/` stays readable in the repository and is linked, not mirrored |

Safety is explained on the site through `SOULMAP.md`'s own ten numbered rules,
which are public doctrine written for exactly that purpose. The site never needs
`skills/safety/` to explain what SoulMap refuses to do.

## Page model

Every `skills/*.md` file already carries YAML front matter with `name` and
`description`. All 77 do, verified. That is the entire schema the site needs. No
new front-matter field is added to canonical content, because website
presentation concerns must not leak into doctrine.

```python
class PublicSection(TypedDict):
    heading: str
    level: int
    anchor: str
    html: str

class PublicPage(TypedDict):
    slug: str            # from filename
    name: str            # front matter
    description: str     # front matter
    category: str        # parent directory
    tier: str | None     # from the SOULMAP.md priority table, frameworks only
    sections: list[PublicSection]
    source_path: str     # for the "view source" link
```

`TypedDict` matches the existing convention in `eval_groups.py` and
`eval_markdown_contracts.py`, so Pyright checks the pipeline end to end.

## Framework tiers

`tier` is parsed from the 27-row priority table in `SOULMAP.md`, matching a
framework's display name to its `Priority` cell. It is never hardcoded. When the
doctrine table changes, the index regroups itself on the next build.

A framework file with no row in that table gets `tier: None` and renders under a
"supporting" group rather than being silently dropped. A row in the table with
no matching public file is reported by the build as a gap, not ignored, because
that mismatch usually means a framework was added to doctrine and the site has
not caught up.

## Required tests

These live in `tests/web/` and run in the standard suite.

**Boundary tests, the ones that matter.**

- Every excluded file above is absent from the build output. Asserted by
  scanning `dist/site/` for each file's distinctive content, not by trusting
  the allowlist to have been applied.
- No rendered page contains a `Detection signals`, `Activation Signals`, or
  `Paired template` heading.
- A sample of real detector phrases, read from
  `src/soulmap/runtime/config/safety.py` at test time rather than hardcoded,
  appears nowhere in the output. Reading them live means the test keeps working
  when the phrase lists change.
- Adding an unlisted file to a temporary `skills/` fixture fails the build.

Each boundary test is verified by the repository's revert-and-confirm-red
standard: temporarily disable the exclusion, watch the test fail, restore it,
watch it pass. A boundary test that cannot fail is the exact bug class
`TESTER.md` Charter 5 names.

**Content tests.**

- Every allowlisted file produces exactly one page.
- Every page has a non-empty `name` and `description`.
- Every internal link in rendered output resolves to a page that exists.
- No page is orphaned from navigation.
- Every framework in the `SOULMAP.md` priority table either has a public page or
  is reported as a known gap.

## Change procedure

Adding a file to the allowlist is a safety-boundary change. It needs the reason
recorded in this document, the boundary tests passing, and, per
`p-level-governance.md`, a pull request declaring `Safety boundary: changed`
with evidence when the file touches doctrine, routing, detectors, guards, or the
shipping boundary.
