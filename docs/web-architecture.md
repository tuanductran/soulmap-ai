# Website architecture

## Boundary

The public site is a self-contained React/Vite static workspace in [`web/`](../web). It consumes public catalog metadata and canonical Markdown at build time, but it is not imported by `soulmap` or `soulmate`. Python runtime/tooling can build and verify artifacts without a browser or Node runtime, while the website deploys as static files without a Python web server.

| Layer | Responsibility |
| --- | --- |
| `web/src/` | React routes, Headless UI interactions, Tailwind visual system, client i18n and local catalog filtering. |
| `web/content/` | Versioned public catalog/prompt metadata used by the static raw-bundle generator. |
| `web/scripts/postbuild.mjs` | Builds locale-specific public Markdown from root `skills/`, sanitizing repository-only references. |
| `web/scripts/verify-static.mjs` | Fail-closed check for routes, raw bundles, assets and banned preview/legacy references. |
| `web/tests/` | Playwright regression coverage for route loading, i18n, provider dialog and raw-bundle handoff. |
| `.github/workflows/website-pages.yml` | Locked Node build, static verification, PR browser audit and `gh-pages` artifact publication. |

## Interaction contract

TanStack Router owns root and locale-prefixed client routes. Headless UI owns focus management and keyboard semantics for menus, disclosure and dialogs. The provider dialog only copies its context-specific prompt and links to the canonical raw bundle; it does not use fragile query-prefill behavior or call a provider API.

The app builds with `SITE_BASE_PATH=/<repository>/` for GitHub Pages. `postbuild.mjs` copies `index.html` to `404.html` so direct static-host routes recover. Asset paths derive from Vite `BASE_URL`, allowing the same source to run at local `/` and production `/soulmap-ai/`.

## Change checklist

When adding a page, update `web/src/router.tsx`, locale-aware navigation if appropriate, English/Vietnamese/Korean content, and browser coverage for interaction changes. When adding a public Skill surface, update both `web/src/content/skills.ts` and the build-time contract in `web/content/`. Run `pnpm --dir web check`, the base-path build, static verifier and browser audit before review.
