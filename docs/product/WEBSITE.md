# SoulMap public website

The public SoulMap website is a **React static application** in [`web/`](../../web). It is a brand and Skill-discovery surface only: SoulMap and Soulmate remain Python domain artifacts, runtime tooling, and importable Markdown packages. The site does not host an AI model, persist a conversation, create accounts, or proxy an external provider.

## Local development and static build

Install the isolated JavaScript workspace and start Vite locally:

```bash
pnpm --dir web install --frozen-lockfile
pnpm --dir web dev
```

GitHub Pages is a project site, so production builds require the repository base path. The build produces the deployable `web/dist/` directory, localized raw Markdown endpoints, and a SPA fallback `404.html`.

```bash
SITE_BASE_PATH=/soulmap-ai/ pnpm --dir web build
pnpm --dir web verify
SITE_BASE_PATH=/soulmap-ai/ pnpm --dir web test:browser
```

| Area | Contract |
| --- | --- |
| Framework | React with TanStack Router and Vite static build. English lives at root; Vietnamese and Korean use `/vi/` and `/ko/`. |
| Styling | TailwindCSS 4 tokens and utilities implement the **Atlas Nội Tâm** editorial field-guide system. |
| Accessible primitives | Headless UI supplies language menus, FAQ disclosure and modal dialog behavior. |
| Static content | `web/content/` contains the public catalog and prompt data used by the build-time raw-bundle generator. |
| Domain source | The raw bundle generator reads canonical Markdown from root `skills/`, sanitizes repository-only references and emits public Markdown only. |
| Public handoff | The provider dialog copies a scoped prompt and offers canonical `/<locale>/api/raw/<slug>.md` links. It never claims a provider will import a Skill automatically. |

## Public routes

The React app preserves English root routes and locale-prefixed Vietnamese/Korean variants for `/`, `/how-it-works`, `/boundaries`, `/notes`, `/skills`, `/about`, `/faq`, `/download`, and `/privacy`. The build also preserves stable raw Markdown URLs at `/api/raw/<slug>.md`, `/vi/api/raw/<slug>.md`, and `/ko/api/raw/<slug>.md`.

Client-side routes are served by `404.html` after a direct GitHub Pages visit. No server-side fallback, htmx fragment endpoint, Python WSGI process, or web API is required.

## GitHub Pages workflow

`.github/workflows/website-pages.yml` installs the locked `web/pnpm-lock.yaml`, builds with the repository base path, runs the static verifier, uploads the built artifact, and runs browser coverage on pull requests. A successful push to `main` publishes only that verified artifact to `gh-pages`. The workflow itself is the deployment automation; contributors must not commit `web/dist/` or manually publish the branch.

## Content and safety boundary

Website copy is public brand content. It may explain reflective use, but it must not diagnose, predict, promise emotional rescue, create dependency, expose repository internals, or imply that SoulMap is a hosted AI service. The static raw endpoint may expose reviewed public Markdown bundles; it must never expose Python source, test files, developer workflow files, credentials, or private material.

The old Python WSGI website was retired in the React migration. New website work belongs under `web/`; Python packages must remain free of a dependency on browser behavior.
