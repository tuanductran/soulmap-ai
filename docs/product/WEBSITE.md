# SoulMap public website

The SoulMap website is a small public brand and Skill-discovery surface served from `src/soulmap/web/`. It is deliberately separate from the runtime Python knowledge loaders and from the generated distribution artifacts, while the public catalog can expose curated Markdown bundles through explicit raw endpoints.

## Run locally

```bash
uv run soulmap web
```

The default address is `http://127.0.0.1:8765`. A different bind address or port can be used for local testing:

```bash
uv run soulmap web --host 0.0.0.0 --port 8765
```

To export a static copy for GitHub Pages or another static host:

```bash
uv run soulmap web --export-static --output site --base-path /soulmap-ai
```

The exporter creates the English and Vietnamese page variants, Skill detail pages, modal partials, catalog JSON, raw Markdown bundles, `static/site.css`, the small `static/site.js` progressive-enhancement layer, and `robots.txt`. The `--base-path` value is optional for a custom domain and should match the repository path when using a GitHub Pages project site.

The server uses Python's standard-library `wsgiref.simple_server`. It does not require a web framework, JavaScript build system, database, account system, or server-side external API. htmx 2.0.10 and Alpine CSP 3.16.2 are loaded from jsDelivr with pinned versions and SRI for progressive enhancement; direct links, server-rendered pages, raw Markdown URLs, and static export remain the fallback when scripts or a CDN are unavailable. Inter is loaded from the official `https://rsms.me/inter/inter.css` stylesheet with system fallbacks.

## Template and asset architecture

The website keeps document markup outside the Python router. `src/soulmap/web/templates/layout.html` owns the shared document shell, metadata, scripts, skip link, main landmark, and footer insertion. `templates/partials/` contains reusable navigation, footer, and Skill-detail fragments; `templates/pages/` contains page-level HTML for home, explanatory pages, download, notes, about, 404, Skill catalog, and Skill detail. `src/soulmap/web/templates.py` provides a small strict `string.Template` renderer from Python's standard library; it intentionally does not attempt to become a general-purpose template language or add a runtime dependency.

Localized copy, route decisions, escaping, card generation, API behavior, and static export remain in Python. `src/soulmap/web/static/site.css` and `src/soulmap/web/static/site.js` are the canonical local assets served at `/static/site.css` and `/static/site.js`. This separation lets designers edit HTML/CSS without searching through a monolithic Python string while preserving the existing WSGI, htmx, Alpine, i18n, and GitHub Pages contracts.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Public positioning and the mirror-first promise |
| `/how-it-works` | Reflection flow and user-ownership explanation |
| `/boundaries` | No-diagnosis, no-prediction, no-dependency and support boundaries |
| `/download` | Links to the generated `.skill` and `.zip` release artifacts |
| `/notes` | Small public-content examples organized by the three content pillars |
| `/about` | Public founder/brand posture without private source-document data |
| `/skills` | Localized catalog of the six public SoulMap Skill groups |
| `/skills/<slug>` | Direct, non-modal detail page for one Skill group |
| `/vi/...` | Vietnamese UI route variants; English remains the default locale |
| `/api/skills.json` | Public catalog metadata for all Skill groups |
| `/api/skills/<slug>.json` | Localized metadata for one Skill group |
| `/api/raw/<slug>.md` | One complete public Markdown bundle for a Skill group |
| `/partials/skill/<slug>.<lang>.html` | Server-rendered htmx modal fragment |
| `/static/site.css` | Responsive local stylesheet |
| `/static/site.js` | Small Alpine CSP component layer |
| `/robots.txt` | Minimal crawl policy |

## Skill catalog and use cases

The catalog presents six complementary surfaces rather than implying that every file should be loaded at once. **Core orchestration** is the starting point for routing and response shape. **Reflective frameworks** are selected after the pattern is clear. **Safety guardrails** remain mandatory whenever risk, crisis, trauma, diagnosis, prediction, or prompt-injection pressure appears. **The grounded symbolic layer** is optional and never predictive. **Voice and calibration** shape delivery without adding authority or dependency. **Brand and positioning** guides public copy and visual coherence.

Each catalog card provides a use-case summary, best-fit description, boundary statement, direct detail page, raw Markdown URL, and best-effort handoff links. Raw links are stable public URLs; they do not authenticate with, upload to, or call an AI provider.

## htmx, Alpine, and modal boundary

The Skill detail modal uses htmx to request a server-rendered HTML fragment and Alpine CSP for local state, filtering, focus return, Escape handling, backdrop close, and a small clipboard action. The modal follows the WAI-ARIA dialog contract: it has `role="dialog"`, `aria-modal="true"`, a visible close control, a focus target, a contained tab sequence, and focus return to the invoking button.

If scripts fail, the card's normal link still opens the same Skill detail page, and the raw Markdown link remains directly usable. The website does not use an SPA, client-side router, local storage, authentication, or a server-side AI integration.

## i18n contract

English is the default public locale. Vietnamese is available through `/vi/...` routes and the language switcher. UI copy is localized in the website surface; raw Skill bundles remain canonical Markdown unless a separately reviewed translated artifact exists. A query parameter such as `?lang=vi` is supported for API/partial requests, while route prefixes are used for shareable pages.

## AI provider handoff contract

The raw URL is the source of truth. ChatGPT and Claude web buttons are best-effort prompt-prefill links and may require sign-in or change behavior outside this repository's control. Claude Code uses the documented `claude-cli://` deep-link scheme where the local environment has registered the protocol. The website therefore always keeps the raw Markdown URL and copy action visible; it never claims that a provider will automatically import a Skill.

## GitHub Pages workflow

The repository workflow builds the static output from `src/soulmap/web/` and performs a static safety check before publishing. The source branch remains the canonical code surface; generated files are never committed to `skills/`, `dist/`, or the Python source package.

Production publication uses the generated `gh-pages` branch because this repository needs a separately inspectable static output branch. In repository Settings, configure GitHub Pages to deploy from the `gh-pages` branch and its root directory. The workflow pushes that branch only after a successful `main` build and verifier run. The branch contains only generated public pages, catalog metadata, raw bundles, static assets, and partials; it is never a source of SoulMap doctrine or runtime code.

## Content boundary

Website copy is public brand content. It may be emotionally resonant, but it must remain accurate about what SoulMap is and is not. Do not add diagnosis, prediction, spiritual certainty, emotional rescue, dependency hooks, or claims about capabilities that are not shipped.

The catalog may expose curated public Skill Markdown because that is an explicit product surface. It must not expose Python source, test files, `.claude/` workflow files, private founder material, credentials, or unrelated repository internals. Provider handoff links must remain ordinary public URLs and must not become platform connectors or authenticated API calls.

## Deliberate non-goals

This website does not implement live AI chat, accounts, a database, memory, analytics, community feeds, numerology calculators, health claims, scheduled reminders, or platform connectors. Adding any of those would require a separate product, privacy, safety, and maintenance decision.

## UX/UI quality contract

The public surface follows a restrained SoulMap visual system rather than copying a component library. Material-style measurable constraints are used for structure and interaction quality, Tailwind-style utilities inform the local token/primitive layer, Bootstrap-style responsive grid and component discipline inform layout, and Apple HIG principles guide clarity, deference to content, legibility, adaptable layout, safe areas, and restrained materials.

| Area | Contract |
| --- | --- |
| Structure | Each public page has one `h1`, meaningful landmark structure, and sequential section/card headings. |
| Contrast | Light and dark tokens are selected for readable text and accent use; the warm gold accent is reserved for an accessible ochre token when it carries meaning. |
| Shape | Content cards use the shared 24px surface radius. The Home mirror card is the single expressive hero exception, using one restrained asymmetric 32px hero token rather than a full capsule or nested outline. |
| Interaction | Keyboard users receive a visible `:focus-visible` ring. Primary controls are at least 48px high and navigation links are at least 44px high. Dialog focus is contained and restored. |
| Adaptation | The layout responds at mobile, tablet, and desktop widths. Narrow navigation remains scrollable rather than shrinking targets below a usable size. Safe-area insets are respected on supported devices. |
| Preferences | `prefers-color-scheme`, `prefers-reduced-motion`, and `prefers-reduced-transparency` are supported without requiring JavaScript. |
| Security | CDN scripts are pinned with SRI, CSP does not use `unsafe-eval`, and static verification rejects local hosts, source code, unapproved scripts, and base-path regressions. |
| Boundaries | No UI addition may introduce live chat, accounts, memory, analytics, database state, platform connectors, or private founder-source data. |

UX changes should be verified with `tests/unit/test_web_server.py`, catalog/API contracts, the static-site verifier, the full repository validation workflow, and visual checks at desktop, tablet, narrow mobile, landscape, dark mode, and keyboard focus states.
