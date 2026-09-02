# SoulMap website

A static site generated from the shipped knowledge package. Nothing here is
authored product copy: every page body comes from `SOULMAP.md`, the root
`SKILL.md`, or `skills/`, so the site cannot say something the package does
not. See [ADR 0005](../docs/engineering/adr/0005-generated-static-site.md).

## Commands

```bash
cd site
npm ci
npm run build   # generate dist/
npm run check   # typecheck, unit tests, build, and validate the generated site
```

## What each file does

| File | Role |
| :--- | :--- |
| `src/content.ts` | Reads the repository and decides what may be published. This is the safety-critical boundary. |
| `src/templates.ts` | Page layout, and resolution of knowledge-base links to site routes. |
| `src/build.ts` | Writes `dist/`. |
| `src/validate.ts` | Re-checks the generated `dist/` for internal leaks and dead links. |
| `src/styles.css` | Design tokens and layout. |
| `tests/content.test.ts` | Pins the publish boundary and link resolution. |

## The publish boundary

`src/content.ts` allows `skills/`, `SKILL.md`, and `SOULMAP.md`, and refuses
every other root. A Markdown link into an internal path, such as `docs/`, is
unwrapped to its text rather than published as a leaking or dead link.

`src/validate.ts` then inspects what actually landed in `dist/`, because the
content layer should not be the only thing preventing a leak.

Adding a file to `skills/` publishes it. Weigh that before moving a file there.

## Deployment

Netlify, configured in `netlify.toml`: build from `site/`, publish `dist/`.
The site is static, with no serverless functions, because nothing here needs a
runtime.
