# SoulMap web architecture

The public SoulMap website uses a small WSGI application with a deliberately narrow entry point. `src/soulmap/web/server.py` keeps the CLI-facing WSGI facade and delegates request work to focused modules. It should not become a page renderer, template engine, asset loader, or catalog implementation.

| Area | Module or directory | Responsibility |
| --- | --- | --- |
| Request dispatch | `src/soulmap/web/routes.py` | Normalize paths, route requests, choose response status and headers. |
| Shared HTTP | `src/soulmap/web/http.py` | Translation lookup, navigation paths, resource hints and secure WSGI responses. |
| Page rendering | `src/soulmap/web/pages.py` | Render localized page content and the shared layout. |
| Skill rendering | `src/soulmap/web/skill_views.py` | Render catalog cards, Skill pages and modal fragments. |
| Asset serving | `src/soulmap/web/assets.py` | Allow-listed text and font assets with safe readers and MIME types. |
| Static export | `src/soulmap/web/exporter.py` | Build localized HTML, API artifacts and static assets for GitHub Pages. |
| Templates | `src/soulmap/web/templates/` | Keep layout, page templates and partials separate from Python rendering logic. |
| Browser assets | `src/soulmap/web/static/` | CSS, JavaScript, favicon and local font files only. |

## Interaction boundaries

AlpineJS owns local UI state such as dropdowns, modal focus, keyboard navigation, clipboard feedback and Skills search mode. htmx owns server-backed fragment requests and progressive same-origin navigation. Normal anchors remain valid fallbacks when JavaScript is unavailable. A new page-level interaction should first be evaluated against these existing boundaries rather than adding another router or client-side framework.

The layout uses htmx boost as an opt-in progressive enhancement at the page shell. Search forms and Skill detail modal triggers explicitly opt out because they have their own client-side or fragment behavior. External provider links, raw Markdown links and downloads remain normal links. The WSGI server continues to return complete HTML documents, so direct requests and static export remain first-class paths.

## Asset policy

Typography is local and served from the allow-listed `/static/fonts/` route. Inter and Manrope files are accompanied by a source notice under `src/soulmap/web/static/fonts/NOTICE.md`. No page template should add a font CDN link or hard-code a third-party font origin. Static export copies the font files and rewrites absolute asset URLs for a GitHub Pages base path.

## Change checklist

When adding a page, add its renderer to `pages.py`, its route contract to `routes.py`, its localized messages to the JSON locale files, and its browser coverage to `tests/browser/`. When adding a browser asset, register it in `assets.py`, serve it through the allow-listed route, include it in `exporter.py`, and add a unit test for its content type and artifact output. Keep `server.py` as a compatibility facade and avoid importing template or asset internals directly into the CLI layer.
