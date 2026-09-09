# Public Site Deployment

The public SoulMap site is a static projection of the shipped knowledge package.
It is generated from `SOULMAP.md`, the root `SKILL.md`, and `skills/` by the
isolated toolchain under `site/`.

## Publish boundary

`site/src/content.ts` is the first boundary: only the shipped knowledge roots
are readable by the site generator. `site/src/validate.ts` is the second
boundary: it inspects generated HTML for repository-only links and dead internal
routes before deployment.

The site is never generated from `docs/`, `templates/`, `.claude/`, tests,
scripts, runtime source, or Library metadata.

## Deployment target

The production target is GitHub Pages through `.github/workflows/site-deploy.yml`.
GitHub's Pages workflow supports custom static generators through
`configure-pages`, `upload-pages-artifact`, and `deploy-pages`; the deployment
job uses the `github-pages` environment and the minimum Pages/OIDC permissions.

The workflow builds only when public-site inputs change and can also be started
manually from Actions.

GitHub Pages must be enabled once in repository settings:

1. Open **Settings → Pages**.
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Protect the `github-pages` environment if additional deployment approval is
   desired.

For a project site, GitHub serves it under the repository path rather than at
account root. The workflow passes the Pages `origin` and `base_path` into the
site generator so canonical URLs, internal links, sitemap, robots.txt, and
assets match the actual published location.

## Publication metadata

Every generated build includes:

- `sitemap.xml`
- `robots.txt`
- `favicon.svg`
- `og-image.svg`
- canonical URL metadata
- `og:url`
- `og:image`

The default site origin is only a local fallback. Production uses the origin
reported by `configure-pages`.

## Rollback

GitHub Pages deployments are tied to workflow runs. To recover from a bad
publication, deploy a known-good `main` commit by re-running the corresponding
successful site-deployment workflow after restoring that commit on the default
branch, or revert the offending commit and let the normal workflow publish the
reverted state.

Do not hot-edit generated `site/dist/` output in the repository. The generated
artifact is disposable; the source knowledge and generator are the sources of
truth.
