# Website architecture

**Status:** Phase 2 proposal, approved for implementation. **Date:** 2026-08-30.

Read [`REPOSITORY-AUDIT.md`](REPOSITORY-AUDIT.md) first. It records the two
findings that shaped everything below, and the owner decisions that resolved
them: amend the maintenance boundary as a scoped exception, and gate all public
content behind an explicit, tested allowlist.

## What the website is

A statically generated public site, built from the repository's own canonical
files, that explains what SoulMap is, how it decides, and where its boundaries
are.

It is a reference and explanation surface. It is not a product interface. A
visitor reads about the mirror principle; they do not talk to a mirror.

## What it is not, and why

| Not | Reason |
| --- | --- |
| A chat or reflection interface | Requires a public API service, which `maintenance-boundary.md` still prohibits. SoulMap belongs inside a consenting conversation on a host platform, not in a page visit |
| A backend service | Nothing on the site needs request-time computation |
| A database-backed app | The content is 77 files in git. A build step is the correct index |
| A single-page application | A reference site that ships HTML is faster, more accessible, and simpler to maintain |
| A mirror of `README.md` | The site derives from doctrine and skills, not from a repository landing page |

## Chosen stack

**Python, Jinja2, static generation.** Option A from the audit.

The decision rests on three facts about this repository, not on preference:

1. `markdown-it-py>=4.2.0` is already a main dependency, so Markdown parsing and
   rendering need nothing new.
2. `src/soulmap/devtools/support/markdown.py` already provides
   `parse_yaml_front_matter`, `slugify_github_anchor`, `strip_inline_markup`,
   `extract_heading_anchors`, and `resolve_local_markdown_target`. A JavaScript
   generator would reimplement all of it, and the two copies would drift.
3. The validation gate is already Python. A Python generator becomes one more
   `soulmap` subcommand inside the existing `lint` run. A Node generator would
   add a second toolchain and a lockfile to a repository with zero Node
   dependencies.

Jinja2 is the only new package. It goes in a `[dependency-groups] web` entry,
following the `awesome-python` precedent, so it never becomes a dependency of
the shipped `soulmap-ai` package. `deptry` verifies that separation.

## Where the code lives

```text
src/soulmap/devtools/web/        generator (Python)
├── __init__.py
├── allowlist.py                 the public-content allowlist, see CONTENT-MODEL.md
├── content.py                   canonical Markdown -> typed model
├── render.py                    model -> HTML via Jinja2
└── build.py                     orchestration, search index, sitemap, robots

website/                         presentation assets (not Python)
├── templates/*.html             Jinja2
└── static/                      style.css, minimal JS, favicon

tests/web/                       generator and content-boundary tests
dist/site/                       build output, git-ignored
```

The split is deliberate. Python under `src/` is automatically covered by Ruff,
Pyright, Vulture, coverage, and `deptry`, because `PYTHON_SOURCE_DIR_NAMES`
already names `src`, `tests`, and `scripts`. A generator living in a new
top-level Python directory would silently sit outside every one of those gates.
Templates and CSS are not Python and do not belong in the wheel, so they live in
`website/`.

`website/` is a new top-level surface, so
[`repo-contract.md`](../engineering/repo-contract.md) gains a row for it in the
same change: purpose "public website presentation assets", scope "published in
the repository, not packaged in either dist archive", validated by the website
tests and the standard Markdown and link gates.

## Data flow

```text
SOULMAP.md            skills/ (allowlisted only)          docs/
      |                        |                            |
      +------------------------+----------------------------+
                               |
                        content.py
              parse front matter, drop internal sections,
                    build typed page models
                               |
                        allowlist.py
              refuse anything not explicitly published
                               |
                         render.py
                   Jinja2 templates -> HTML
                               |
                         build.py
        pages + search-index.json + sitemap.xml + robots.txt
                               |
                          dist/site/
```

One direction only. The website reads canonical files and never writes them.
There is no `website/content/` tree, so content drift is structurally
impossible rather than merely discouraged.

## Routes

Derived from what the repository can actually support, not from a template.

| Route | Source | Notes |
| --- | --- | --- |
| `/` | `SOULMAP.md`, `skills/brand/` | Identity, mirror principle, entry points |
| `/frameworks/` | allowlisted `skills/frameworks/` | Index, grouped by priority tier |
| `/frameworks/<slug>/` | one allowlisted framework file | Public prose only |
| `/safety/` | `SOULMAP.md` safety rules | The 10 rules as public doctrine |
| `/architecture/` | `SOULMAP.md`, `library-vs-framework.md` | How routing and enforcement actually work |
| `/about/` | `skills/brand/` allowlisted files | Positioning, what SoulMap refuses to be |
| `/search/` | generated index | Progressive enhancement over the index page |
| `/404.html` | static | |

No `/docs` route. `docs/` is contributor and operator documentation that already
lives readable in the repository. Mirroring it onto the site would duplicate
content the audit's drift rule forbids duplicating, and would put maintainer
material on a public product surface. The site links to the repository instead.

No `/library` route in this phase. `dist/soulmap-ai-library.json` is
distribution metadata for a manual install flow, not public reading material.

## The priority hierarchy is the site's spine

`SOULMAP.md` already contains a 27-row priority table ordering every framework
from Crisis down to Mirror. That table is the most honest possible information
architecture for the frameworks index: it is how SoulMap actually decides, it is
already canonical, and it needs no invented taxonomy.

Framework grouping on the site therefore uses the real tiers, Highest through
Default, parsed from that table. When the table changes, the site regroups
itself.

## Search

Build time writes `search-index.json` from the public model: title, category,
tier, description, and public prose text. The client filters it.

Progressive enhancement is required. The frameworks index renders every entry as
static HTML; JavaScript hides non-matching entries with the `hidden` attribute.
With JavaScript disabled the full index is still readable and navigable. No
server, no search service, no runtime dependency.

## Build and validation

A new CLI command, `soulmap build-site`, joins `_command_table()` in `cli.py`.
Per the `cli-tooling-maintainer` rule the command surface is a stability
contract, so this is one command with a clear need, not a family of flags.

```bash
uv run soulmap build-site            # writes dist/site/
uv run soulmap build-site --check    # build and assert boundaries, no write
```

`--check` runs in CI and in `soulmap lint`, so a change that would publish an
unlisted file fails the same gate that already catches Markdown drift.

## Deployment

Out of scope for this change. The build produces a static directory; publishing
it is a separate decision with its own trigger. Nothing in the architecture
assumes a host, and no deployment configuration ships in this phase.

## What stays unchanged

`skills/` remains the shipped knowledge source. `src/soulmap/runtime/` remains
the runtime source of truth and is explained by the site, never executed by it.
`dist/soulmap-ai.zip` and `dist/soulmap-ai.skill` keep exactly their current
contents. `.claude/` and `templates/` stay unpublished. The wheel keeps its
current meaning.
