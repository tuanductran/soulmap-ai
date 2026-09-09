# ADR 0005: The Website Is Generated From the Shipped Package

- Status: Accepted
- Date: 2026-09-02
- Related: [`repo-contract.md`](../repo-contract.md),
  [`maintenance-boundary.md`](../maintenance-boundary.md)

## Context

SoulMap had no public web presence. The knowledge base is Markdown, so it is
readable on GitHub, but that surface shows a repository rather than a product,
and it makes no distinction between what ships and what is internal.

Adding a website raises two problems this repository has already decided
elsewhere, and one that is new.

**Drift.** A hand-written marketing site becomes a second description of what
SoulMap does. The repository already forbids that shape: `repo-contract.md`
names one source of truth per surface, and the working rules say to prefer
updating an existing file over creating a parallel one. A site that restates
the doctrine in its own words is a parallel file with a nicer font.

**The shipped boundary.** `docs/`, `templates/`, `.claude/`, `tests/`,
`scripts/`, `src/`, `evals/`, and `library/` never ship. `templates/` in
particular holds internal brand and marketing copy, which is exactly the
material a website is otherwise tempted to reach for. Publishing is a wider
disclosure than packaging: a build artifact goes to someone who installed the
skill, while a page goes to anyone.

**A new toolchain.** The repository is Python, gated by `uv` and a fixed set of
commands. A site needs Node. Mixing them risks slowing or breaking gates that
have nothing to do with the site.

## Decision

Add `site/`, a static site generated from the shipped knowledge package, and
keep it fully self-contained.

**Every page is generated.** The site authors no product claims. Page bodies
come from `SOULMAP.md`, the root `SKILL.md`, and `skills/`. Chrome copy, such
as the navigation and the footer, is the only hand-written text, and it makes
no claim the doctrine does not already make. Correcting a page means correcting
the file it came from.

**The shipped boundary is the publish boundary.** `site/src/content.ts` allows
`skills/`, `SKILL.md`, and `SOULMAP.md`, and refuses everything else by
explicit root. A link into an internal path is unwrapped to its text rather
than rendered as a dead or leaking link. `site/src/validate.ts` then re-checks
the generated `dist/` for internal link roots and dead links, because the
content layer should not be the only thing preventing a leak.

**The toolchain stays inside `site/`.** Its own `package.json`, lockfile, and
CI job. `site/` is excluded from the shipped archives and is not read by
`ruff`, `pyright`, or `deptry`. The Python gates are untouched.

## Rationale

Generating the site is what makes the drift problem structural rather than a
discipline problem. There is no place to write a claim that the package does
not make, because there is no authored page body to write it in.

Enforcing the publish boundary in two places is deliberate, and follows the
same reasoning as ADR 0001's layered detection: the content layer decides what
may be read, and the validator checks what actually landed. The second check
found real defects the first did not, twice, during the initial build.

Keeping the toolchain isolated follows `performance-tooling.md`. The Python
gates are the ones run on every change; a Node install in their path would tax
every contributor for a surface most changes do not touch.

## Alternatives Considered

**A hand-written marketing site.** Rejected. It creates the second description
of SoulMap that this repository is organized to avoid, and it is the shape most
likely to reach for `templates/` copy.

**Publishing `docs/` as the site.** Rejected. `docs/` is contributor and
operator documentation, written for people working on SoulMap. It is not
wrong, but it is not the product, and publishing it presents internal
engineering process as the public face.

**Server-side rendering or serverless functions.** Rejected as unearned. The
content is static and changes only when the package changes. A function
introduces a runtime, a failure mode, and a second place where behavior could
diverge from the package, in exchange for nothing this site needs.

**A Python static generator, to keep one toolchain.** Rejected. It would put
presentation logic into `src/`, which the working rules reserve for
orchestration, detection, and enforcement, and it would make the Python gates
responsible for HTML.

## Consequences

- `site/` is a new repository surface, recorded in `repo-contract.md`. It is
  local-only and never packaged.
- Adding a skill or a document publishes a page automatically. No site change
  is needed, and none is possible without editing the source file.
- The publish boundary has tests of its own. `site/tests/content.test.ts` pins
  the refused roots, traversal, and link resolution directly, rather than only
  through a full build.
- Changing what ships changes what publishes. Anything moved into `skills/`
  becomes public on the next deploy, which is a consequence a contributor must
  weigh before moving a file there.
- CI gains one Node job. The Python gates keep their current shape and runtime.
