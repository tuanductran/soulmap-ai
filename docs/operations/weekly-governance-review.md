# Weekly governance and dependency review

The weekly GitHub Actions workflow runs every Monday at 05:17 UTC and can be started
manually. It is a deterministic review of the current default branch; it never updates a
dependency, merges a pull request, changes a tag or creates a release.

## What the review verifies

| Area | Evidence produced |
| --- | --- |
| P-level governance | Contract tests confirm priority metadata, safety-boundary evidence, rollback language, workflow and P1 plan remain connected. |
| Dependency hygiene | `uv lock --check`, a captured direct dependency tree and Deptry confirm the locked baseline remains coherent. |
| Safety/knowledge baseline | Markdown contract, links, case, lint, knowledge audit, safety evals, grouped evals, response evals and Markdown contract evals all run. |
| Test reproducibility | The full suite runs through `pytest_diagnostics.py`, preserving the seed and serial reproduction details on failure. |
| Distribution integrity | ZIP, skill and Library manifest artifacts are rebuilt and verified by hash and extraction boundary. |

The uploaded `weekly-governance-evidence` artifact contains the direct dependency tree and,
when the build reaches that stage, the generated distribution artifacts. Review the
workflow summary and artifact before deciding whether a Dependency Dashboard item has a
real maintenance trigger.

## What it does not do

The schedule does not poll external services, classify content with a model, create a
dependency update, alter the lockfile, open a pull request, merge a branch or publish a
release. A real advisory, deprecation, incompatibility, lock drift or maintenance window
still starts the bounded P1 process in
[`dependency-refresh.md`](dependency-refresh.md).

## Operating response

When the weekly review passes, no action is required. When it fails, first preserve the
workflow URL, failing command, Python/OS context, lock state and pytest seed if shown.
Then open one issue that names the trigger and follow the relevant P-level path. Do not
weaken a safety check or rerun until green without recording why the failure occurred.
