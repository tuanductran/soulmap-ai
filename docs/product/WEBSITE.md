# SoulMap AI website

The SoulMap website is a small public brand surface served from `src/soulmap/web/`.
It is deliberately separate from the shipped `skills/` knowledge base, the Python runtime
knowledge loaders, and the generated `dist/soulmap-ai.skill` and `dist/soulmap-ai.zip`
artifacts.

## Run locally

```bash
uv run soulmap web
```

The default address is `http://127.0.0.1:8765`. A different bind address or port can be
used for local testing:

```bash
uv run soulmap web --host 0.0.0.0 --port 8765
```

To export a static copy for GitHub Pages or another static host:

```bash
uv run soulmap web --export-static --output site --base-path /soulmap-ai
```

The exporter creates `index.html`, one directory index for each public route, `static/site.css`,
and `robots.txt`. The `--base-path` value is optional for a custom domain and should match
the repository path when using a GitHub Pages project site.

The server uses Python's standard-library `wsgiref.simple_server`. It does not require a
web framework, JavaScript bundle, database, account system, external API, or runtime
service. It is a local/public-static presentation surface, not an AI conversation API.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Public positioning and the mirror-first promise |
| `/how-it-works` | Reflection flow and user-ownership explanation |
| `/boundaries` | No-diagnosis, no-prediction, no-dependency and support boundaries |
| `/download` | Links to the generated `.skill` and `.zip` release artifacts |
| `/notes` | Small public-content examples organized by the three content pillars |
| `/about` | Public founder/brand posture without private source-document data |
| `/static/site.css` | Embedded responsive stylesheet served by the Python app |
| `/robots.txt` | Minimal crawl policy |

## GitHub Pages workflow

The repository workflow builds the static output from `src/soulmap/web/` and performs a
static safety check before publishing. The source branch remains the canonical code
surface; generated files are never committed to `skills/`, `dist/`, or the Python source
package.

Production publication uses the generated `gh-pages` branch because this repository
needs a separately inspectable static output branch. In the repository Settings, configure
GitHub Pages to deploy from the `gh-pages` branch and its root directory. The workflow
pushes that branch only after a successful `main` build and verifier run. The branch contains
only static output and is never a source of SoulMap doctrine or runtime code.

GitHub's artifact-based Pages Actions remain a valid future alternative, but they are not
used here because the requested operating boundary is an inspectable `gh-pages` branch.

## Content boundary

Website copy is public brand content. It may be emotionally resonant, but it must remain
accurate about what SoulMap is and is not. Do not add diagnosis, prediction, spiritual
certainty, emotional rescue, dependency hooks, or claims about capabilities that are not
shipped.

The website must not expose repository internals such as `src/`, `tests/`, `.claude/`,
engineering documentation, runtime implementation paths, or private founder material. It
may link to the public GitHub repository and release page, but the AI import surface
remains the generated `.skill` or `.zip` artifact.

## Deliberate non-goals

This first website surface does not implement live AI chat, accounts, a database, memory,
analytics, community feeds, numerology calculators, health claims, scheduled reminders, or
platform connectors. Adding any of those would require a separate product, privacy, safety,
and maintenance decision.
