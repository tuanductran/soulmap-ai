# Soulmate OIDC Trusted Publishing

## Scope and status

This guide describes a future, maintainer-approved path for publishing the executable `soulmate-ai` Python package to TestPyPI or PyPI through GitHub Actions OpenID Connect (OIDC). It does not authorize publication and does not apply to the AI-facing `soulmate-ai.zip` or `soulmate-ai.skill` files.

PyPI Trusted Publishing uses OIDC to exchange a short-lived CI identity for a project-scoped upload token. PyPI documents that the resulting token expires automatically after a short period, which avoids storing a long-lived API token in GitHub repository secrets.[1]

The repository must keep this path disabled until the package name, owner, workflow filename, environment, version strategy, and publication approval are recorded in the release evidence.

## Distribution surfaces

| Surface | Intended destination | Authentication path |
| --- | --- | --- |
| `soulmate_ai-<version>-py3-none-any.whl` | TestPyPI/PyPI | OIDC Trusted Publishing |
| `soulmate_ai-<version>.tar.gz` | TestPyPI/PyPI | OIDC Trusted Publishing |
| `soulmate-ai.zip` | Manual GitHub Release or reviewed artifact handoff | GitHub release permissions, if separately approved |
| `soulmate-ai.skill` | Manual GitHub Release or reviewed artifact handoff | GitHub release permissions, if separately approved |

A Python package upload must never be inferred from a successful AI skill artifact build. The wheel/sdist builder and the AI skill builder have different allow-lists, verification commands, and release decisions.

## Required decisions before configuration

Do not configure a Trusted Publisher until a maintainer has recorded all of the following:

| Decision | Required value or evidence |
| --- | --- |
| Package name | The approved PyPI project name, currently proposed as `soulmate-ai` |
| Project owner | The PyPI account or organization that owns the project |
| Repository | `tuanductran/soulmap-ai` |
| Publishing workflow | The exact workflow filename, recommended: `soulmate-pypi-release.yml` |
| GitHub environment | Recommended protected environment: `pypi` |
| Version policy | One-time immutable release versions with a documented pre-release policy |
| Test index | A separate TestPyPI Trusted Publisher configuration, if used |
| Approval | Explicit maintainer approval for the first TestPyPI and PyPI publication |
| Rollback | Registry yank/withdrawal process and corrected-version plan |

The workflow filename is part of the trust relationship. Renaming the file, moving the publish job to another workflow, or changing the environment can invalidate the configured relationship or create an unintended trust gap.

## Security model

GitHub Actions issues an OIDC identity token only to a job with `id-token: write`. PyPI matches the token against the Trusted Publisher configuration for the project. GitHub's documentation recommends linking the PyPI project to the exact repository and workflow, and recommends protecting the GitHub environment used for publication.[3]

Use the permission only at the publishing job level:

```yaml
permissions:
  contents: read

jobs:
  pypi-publish:
    permissions:
      contents: read
      id-token: write
```

Do not grant `id-token: write` to pull request, build, lint, test, or artifact-review jobs. Do not place a PyPI token, password, or OIDC token in repository variables, logs, Markdown, or committed files. The PyPA publishing action obtains the OIDC credential without a manually managed `PYPI_TOKEN`.[2]

## Configure PyPI

### Existing PyPI project

After the package name and owner are approved, sign in to PyPI with the owning account and open the project's publishing settings:

```text
https://pypi.org/manage/project/soulmate-ai/settings/publishing/
```

Add a GitHub Actions Trusted Publisher with these values:

| PyPI field | SoulMap repository value |
| --- | --- |
| Owner | `tuanductran` |
| Repository name | `soulmap-ai` |
| Workflow name | `soulmate-pypi-release.yml` |
| Environment name | `pypi` |

The owner, repository, workflow, and environment values must match the final workflow exactly. An incorrect mapping is equivalent to giving the wrong workflow publishing authority for the project.[3]

### New PyPI project

If the project does not exist, use PyPI's documented project-creation flow for a Trusted Publisher rather than creating a long-lived API token as a temporary shortcut. Confirm that the chosen package name is approved and available before creating or reserving any project identity.

Do not create the project merely to test this repository. Project creation, pending publisher setup, and the first publication are maintainer-controlled release actions.

### TestPyPI

TestPyPI has a separate project namespace and separate Trusted Publisher configuration. Configure the same repository and exact workflow name on TestPyPI before using it:

```text
https://test.pypi.org/manage/project/soulmate-ai/settings/publishing/
```

Use a distinct protected GitHub environment such as `testpypi` if both indexes are configured. The publishing action must receive the TestPyPI repository URL explicitly. Do not assume that a PyPI trust configuration automatically applies to TestPyPI.

## Configure GitHub environment protection

Create a `pypi` environment in the repository settings before enabling the publishing job. Configure:

- required reviewer approval for deployment;
- deployment branch or tag rules limited to the approved release ref;
- no deployment rule that permits arbitrary pull request branches;
- notifications for rejected or completed deployments;
- environment secrets only if a later, separately approved integration needs them.

OIDC Trusted Publishing itself should not require a PyPI password or repository secret. The environment is a human approval and branch restriction boundary, not a place to store an API token.

## Recommended future workflow shape

The following is a preparation example. It is not enabled by this guide. The publishing action reference must be replaced with a reviewed, full commit SHA before the workflow is committed. Do not copy a floating third-party action tag into a production release workflow without a pin review.

```yaml
name: Soulmate PyPI release

on:
  workflow_dispatch:
    inputs:
      publish:
        description: Publish the verified Soulmate Python package
        required: true
        default: false
        type: boolean

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<reviewed-full-commit-sha>

      - uses: ./.github/actions/setup-uv
        with:
          python-version: "3.11"

      - name: Install locked development environment
        run: uv sync --locked --python 3.11

      - name: Build isolated Soulmate Python distributions
        run: uv run python scripts/build_soulmate.py --output-dir dist/soulmate

      - name: Verify Python distributions
        run: |
          uv run python scripts/verify_soulmate_package.py \
            --wheel dist/soulmate/soulmate_ai-0.1.0-py3-none-any.whl \
            --sdist dist/soulmate/soulmate_ai-0.1.0.tar.gz \
            --version 0.1.0

      - name: Upload verified Python distributions
        uses: actions/upload-artifact@<reviewed-full-commit-sha>
        with:
          name: soulmate-python-dists-${{ github.sha }}
          path: dist/soulmate/
          if-no-files-found: error

  pypi-publish:
    if: inputs.publish == true
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Retrieve verified Python distributions
        uses: actions/download-artifact@<reviewed-full-commit-sha>
        with:
          name: soulmate-python-dists-${{ github.sha }}
          path: dist/soulmate/

      - name: Publish to PyPI with Trusted Publishing
        uses: pypa/gh-action-pypi-publish@<reviewed-full-commit-sha>
        with:
          packages-dir: dist/soulmate/
```

The build job must produce the exact files consumed by the publish job. The publish job must not rebuild from a different checkout or accept arbitrary paths. The final workflow should also run the package verifier after downloading the artifact and before the publishing action.

The repository's current `soulmate-release.yml` workflow is a manual package/release preparation workflow and does not by itself establish PyPI Trusted Publishing. Do not add `id-token: write` to that workflow casually. Prefer a separately reviewed workflow whose filename, environment, and permissions are dedicated to PyPI publication.

## TestPyPI trial sequence

Use the following sequence for the first external trial:

1. Merge the reviewed builder, verifier, manifest, CI, contribution guide, and release documentation changes.
2. Confirm the package version, distribution names, and final source commit.
3. Configure the TestPyPI Trusted Publisher with the exact repository, workflow filename, and protected `testpypi` environment.
4. Run the workflow with the explicit publish input enabled only after a maintainer approves the deployment.
5. Verify the TestPyPI project page and install the uploaded wheel in a clean Python 3.11 environment.
6. Confirm metadata, imports, version, and package boundary independently from the AI skill artifact.
7. Record the workflow run, TestPyPI project URL, package version, files, sizes, and hashes.
8. Decide whether the result is sufficient evidence for the PyPI release gate.

TestPyPI is a separate index, not a private mode of PyPI. A successful TestPyPI upload does not prove that the PyPI Trusted Publisher configuration is correct.

## Official PyPI release sequence

Before PyPI publication:

- [ ] The package identity and namespace are approved.
- [ ] The final version has never been published to PyPI.
- [ ] The release commit is on the approved branch or tag.
- [ ] The exact wheel and sdist pass `verify_soulmate_package.py`.
- [ ] The package has passed the repository's full required test and quality gates.
- [ ] The PyPI Trusted Publisher matches the exact owner, repository, workflow, and environment.
- [ ] The `pypi` environment has required reviewers and deployment restrictions.
- [ ] The publish job alone has `id-token: write`.
- [ ] The publishing action is pinned to a reviewed full commit SHA.
- [ ] No PyPI password or API token is present in the workflow.
- [ ] The package distributions are downloaded from the verified build artifact.
- [ ] The maintainer has explicitly approved the publication.

Run the workflow once. Do not retry a successful upload for the same version merely because a later metadata check is inconvenient. Investigate the result first; package files for an existing version are normally immutable.

## Troubleshooting matrix

| Symptom | Likely cause | Safe response |
| --- | --- | --- |
| OIDC token unavailable | Missing job-level `id-token: write` or publishing job not running in GitHub Actions | Check job permissions; do not add a repository token as an unreviewed workaround |
| Trusted Publisher not found | Owner, repository, workflow filename, or environment mismatch | Compare the final YAML and PyPI settings character-for-character |
| Environment approval never appears | Environment name mismatch or workflow did not reach the publish job | Check `needs`, `if`, environment name, and deployment rules |
| Upload rejected as existing version | Version already exists on the index | Stop; choose a new corrected version rather than replacing files |
| TestPyPI works but PyPI fails | The two indexes have independent projects/configurations | Configure and review PyPI separately |
| Artifact missing or wrong | Publish job rebuilt or downloaded the wrong artifact | Re-run build/verify; do not publish until exact artifact parity is proven |
| Token appears in logs | Unsafe manual exchange or unmasked output | Stop publication, rotate/revoke affected credentials, review run logs |

Do not use the manual OIDC token exchange commands from implementation documentation in the production workflow unless a separate security review explicitly requires them. The stable PyPA publishing action is the preferred integration path.[2]

## Rollback and incident handling

If a package has a content or security issue, do not upload a replacement file under the same version. Disable the GitHub environment, suspend the publishing workflow, review the run and project history, and use the registry's documented yank or withdrawal process. Publish a corrected higher version only after the verifier and release checklist pass again.

If the Trusted Publisher mapping is wrong, treat it as a credential-equivalent incident. Remove or narrow the PyPI trust configuration, disable the `pypi` environment, review all recent workflow runs, and confirm that no unexpected project was modified.

If a token or secret is exposed, stop all publication activity and rotate or revoke it before continuing. OIDC is designed to avoid long-lived PyPI tokens, but it does not remove the need to protect workflow permissions, environment approvals, action pins, and source review.

## Current non-goals

This guide does not:

- enable OIDC in the repository;
- create a PyPI or TestPyPI project;
- create GitHub environments;
- add `id-token: write` to a workflow;
- add a PyPI publishing action to the current release workflow;
- publish the Python package;
- publish the AI `.zip` or `.skill` artifact;
- define a public registry namespace without maintainer approval.

### References

[1]: https://docs.pypi.org/trusted-publishers/ "PyPI: Publishing to PyPI with a Trusted Publisher"
[2]: https://docs.pypi.org/trusted-publishers/using-a-publisher/ "PyPI: Publishing with a Trusted Publisher"
[3]: https://docs.GitHub.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi "GitHub: Configuring OpenID Connect in PyPI"
