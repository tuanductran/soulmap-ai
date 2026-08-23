# Soulmate release checklist

## Purpose

This checklist governs an official release of Soulmate after the P0, P1, P2, P3-A, and PR-CI changes have been reviewed and merged. It separates the executable `soulmate-ai` Python package from the AI-facing foundation-skill artifacts. They may share a release decision, but they are different distribution surfaces and must be verified independently.

> A successful CI build is evidence that an artifact passed the repository contract. It is not permission to create a release, publish to PyPI, or activate an AI-tool distribution.

## Release surfaces

| Surface | Output | Distribution method | Current state |
| --- | --- | --- | --- |
| Python library | `soulmate_ai-<version>-py3-none-any.whl`, `soulmate_ai-<version>.tar.gz` | Future PyPI/TestPyPI Trusted Publishing | Pre-release; no registry publication authorized |
| AI foundation skills | `soulmate-ai.zip`, `soulmate-ai.skill` | Manual GitHub Release or reviewed artifact handoff | Built and verified in PR CI; no public release authorized |
| Review metadata | `manifest.json`, `PROVENANCE.json`, `SHA256SUMS` | CI artifact and release attachment | Generated for review; must match final bytes |

Do not describe the AI `.zip` or `.skill` as a Python package. Do not place Python source in the AI skill artifact. Do not use the SoulMap root artifact builder for Soulmate artifacts.

## Release roles and approval

A release requires a maintainer who owns the version decision, a reviewer who checks package and artifact boundaries, and an operator who runs the approved workflow. One person may hold all roles, but the checklist must still record each decision explicitly.

The following actions require explicit maintainer approval and must never be triggered by a pull request workflow:

- changing the pre-release distribution status;
- creating a Git tag or GitHub Release;
- publishing `soulmate-ai` to TestPyPI or PyPI;
- enabling `id-token: write` in a publishing job;
- changing the PyPI Trusted Publisher configuration;
- changing the artifact allow-list, manifest schema, or source-of-truth boundary.

## A. Pre-release readiness

### Baseline and review

- [ ] PRs #245, #246, #248, #249, #250, #251, and #252 are reviewed and merged in dependency order, or their final merged equivalents are recorded.
- [ ] `main` is the release baseline and the checkout has no unexplained local changes.
- [ ] The intended release commit is identified and recorded.
- [ ] The Soulmate package version in `packages/soulmate/pyproject.toml` is the intended version.
- [ ] Every selected skill entry uses the intended collection version in `packages/soulmate/skills/manifest.json`.
- [ ] The release note identifies whether the release contains Python package changes, AI skill content changes, or both.
- [ ] The release does not silently include SoulMap doctrine, root Skills, safety policy, voice, brand, spiritual content, website files, or private repository data.

### Version and compatibility

- [ ] Package version, skill collection version, manifest schema version, and SoulMap framework version are recorded separately.
- [ ] Compatibility ranges are reviewed for every manifest entry.
- [ ] A breaking public contract change has a migration note and an appropriate version decision.
- [ ] The version has not already been uploaded to the selected registry. Python package registries do not generally permit replacing an existing distribution file for the same version.
- [ ] The changelog or release note explains changed contracts, added skills, removed skills, and known limitations.

## B. Clean build and artifact verification

Run these commands from a clean checkout at the approved commit:

```bash
uv sync --locked --python 3.11
uv run soulmap format
uv run soulmap lint --skip-tests
uv run soulmap markdown-contract --root .
uv run soulmap check-links --root .
uv run soulmap check-case --root .
uv run soulmap check-dependencies --root .
uv run soulmap test -n auto -q
```

Build the Python package separately:

```bash
rm -rf dist/soulmate
uv run python scripts/build_soulmate.py --output-dir dist/soulmate
uv run python scripts/verify_soulmate_package.py \
  --wheel dist/soulmate/soulmate_ai-<version>-py3-none-any.whl \
  --sdist dist/soulmate/soulmate_ai-<version>.tar.gz \
  --version <version>
```

Build and verify the AI foundation-skill artifacts separately:

```bash
rm -rf dist/soulmate-skills
uv run python scripts/build_soulmate_skills.py \
  --output-dir dist/soulmate-skills \
  --source-commit <approved-commit>
uv run python scripts/verify_soulmate_skills.py \
  --zip dist/soulmate-skills/soulmate-ai.zip \
  --skill dist/soulmate-skills/soulmate-ai.skill \
  --checksums dist/soulmate-skills/SHA256SUMS \
  --version <skill-version>
```

### Artifact inspection

- [ ] Both AI projections are byte-identical.
- [ ] A second clean build produces identical `.zip` and `.skill` bytes.
- [ ] The archive contains only `README.md`, `LICENSE`, `artifact-contract.md`, `manifest.json`, `PROVENANCE.json`, and manifest-selected `skills/foundation/*.md` files.
- [ ] The archive contains no `src/`, `src/soulmap/`, root SoulMap `skills/`, `reference/`, `.claude/`, `.github/`, tests, website output, Python source, lockfile, or local build state.
- [ ] Manifest entries, provenance file list, manifest digest, artifact version, and selected IDs agree.
- [ ] `SHA256SUMS` matches the final `.zip` and `.skill` bytes.
- [ ] ZIP member paths, duplicate names, symlink-like entries, size limits, Markdown front matter, and high-confidence secret markers have been checked.
- [ ] The Python wheel/sdist contains the intended `src/soulmate/` implementation and does not claim to be the AI skill import surface.
- [ ] The generated files are preserved as CI/release evidence, not edited manually.

## C. Release channel decision

Before a release workflow is run, record one of the following decisions:

| Decision | Required action |
| --- | --- |
| Review-only | Upload CI artifacts only. Do not create a release or publish a registry package. |
| GitHub Release for AI skills | Review final `.zip`, `.skill`, manifest, provenance, and checksums, then run the separately approved manual release workflow. |
| TestPyPI package trial | Configure TestPyPI Trusted Publishing, use a protected environment, publish the exact verified wheel/sdist, and test installation in a clean environment. |
| PyPI package release | Complete TestPyPI or equivalent acceptance, configure PyPI Trusted Publishing, publish the exact verified wheel/sdist once, and record the resulting project URL. |
| Combined release | Complete the GitHub Release and PyPI gates independently. One successful surface does not waive the other surface's checks. |

The existing manual Soulmate package workflow is not a public registry authorization. It must remain non-publishing until the package name, trusted publisher, workflow, environment, and approval are confirmed. The dedicated `.github/workflows/soulmate-pypi-release.yml` workflow is the staged TestPyPI OIDC path; it remains fail-closed until its explicit repository variables and package-visibility decision are approved.

## D. GitHub Release gate for AI skills

- [ ] The release commit is on the approved branch and matches the reviewed source.
- [ ] The workflow is run from the approved ref, not from an unreviewed pull request merge ref.
- [ ] The final AI artifacts are built and verified in the workflow.
- [ ] The release title/tag uses the agreed Soulmate version strategy and does not collide with a prior tag.
- [ ] The GitHub Release notes identify the AI artifact files and their SHA-256 digests.
- [ ] No Python wheel/sdist is attached as an AI skill file unless the release note labels it separately.
- [ ] The release is marked pre-release if the maintainer has not approved public stability.
- [ ] The release URL, tag, artifact names, sizes, and digests are recorded in the release evidence.

## E. PyPI Trusted Publishing gate

Complete the separate [Soulmate OIDC Trusted Publishing guide](SOULMATE-OIDC-TRUSTED-PUBLISHING.md) before enabling any PyPI publishing job.

- [ ] The exact PyPI project name has been approved and is available or already owned.
- [ ] The PyPI Trusted Publisher configuration names this repository and the exact release workflow file.
- [ ] The GitHub environment name in the PyPI configuration exactly matches the workflow environment, if one is used.
- [ ] The environment has required reviewers and deployment restrictions appropriate for releases.
- [ ] The publishing job has job-level `id-token: write`; build and pull request jobs do not have it.
- [ ] The publishing action is pinned to a reviewed full commit SHA.
- [ ] No `PYPI_TOKEN`, password, or manually generated API token is stored in repository secrets for the Trusted Publishing path.
- [ ] The workflow does not publish from `pull_request`, forks, arbitrary branches, or unreviewed tags.
- [ ] `soulmate-pypi-release.yml` is manually dispatched from `main` and the publication gate requires `SOULMATE_PUBLICATION_ENABLED=true` and `SOULMATE_PUBLICATION_TARGET=testpypi`.
- [ ] The `testpypi` environment has required reviewers and deployment restrictions before the publish job is enabled.
- [ ] The uploaded distributions are the same files that passed package verification.
- [ ] The release log does not print tokens or private configuration.
- [ ] The current `Private :: Do Not Upload` classifier has been deliberately removed in a separate release decision before the first package publication.

## F. Post-release verification

- [ ] GitHub Release assets can be downloaded and verified against recorded SHA-256 values.
- [ ] The AI archive extracts successfully in a clean directory and contains the expected file set.
- [ ] If PyPI was used, the project page shows the intended version and metadata.
- [ ] A clean Python 3.11 environment installs the exact wheel from the selected index and imports the intended public package.
- [ ] The AI skill artifact and Python package are tested independently after download.
- [ ] The release evidence records workflow run ID, commit, tag, version, artifacts, digests, reviewer, and publication result.
- [ ] The next version is not opened until the current release evidence is complete.

## G. Rollback and incident response

A published Python distribution cannot be replaced by uploading a different file with the same version. If a package is compromised or incorrect, follow the registry's documented yank or withdrawal process, publish a corrected higher version, and document the affected version. Do not delete evidence or rewrite the release history.

For a GitHub Release, mark the release as draft or pre-release, remove or supersede assets according to the maintainer decision, and publish a corrected release/tag only after the artifact verifier passes. If the issue is a boundary leak, stop all further distribution and rotate any exposed credential before investigating the content.

For any OIDC or workflow incident, disable the publishing environment, remove or narrow the PyPI Trusted Publisher configuration, review recent workflow runs, and inspect the published project history. Treat an incorrect repository/workflow/environment trust mapping as a credential-equivalent incident.

## Final sign-off

- [ ] Content owner sign-off complete.
- [ ] Package boundary reviewer sign-off complete.
- [ ] Artifact/security reviewer sign-off complete.
- [ ] Release operator sign-off complete.
- [ ] Explicit maintainer approval recorded for each mutating action.
- [ ] No release, tag, registry publication, or provider activation remains pending without an owner.

### References

[1]: https://docs.pypi.org/trusted-publishers/ "PyPI: Publishing to PyPI with a Trusted Publisher"
[2]: https://docs.pypi.org/trusted-publishers/using-a-publisher/ "PyPI: Publishing with a Trusted Publisher"
[3]: https://docs.GitHub.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi "GitHub: Configuring OpenID Connect in PyPI"
