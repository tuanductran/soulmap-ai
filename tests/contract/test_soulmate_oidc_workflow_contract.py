"""Contracts for the gated Soulmate TestPyPI OIDC workflow."""

from __future__ import annotations

from soulmap.devtools.support.repo import REPO_ROOT

WORKFLOW = REPO_ROOT / ".github" / "workflows" / "soulmate-pypi-release.yml"
MANUAL_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "soulmate-release.yml"
PUBLISH_ACTION_SHA = "dc37677b2e1c63e2034f94d8a5b11f265b73ba33"


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_oidc_workflow_is_manual_and_main_only() -> None:
    workflow = _workflow()

    assert "workflow_dispatch:" in workflow
    assert "if: github.ref == 'refs/heads/main'" in workflow
    assert "if: inputs.publish == true" in workflow
    assert "concurrency:" in workflow
    assert "cancel-in-progress: false" in workflow


def test_build_and_publish_jobs_use_exact_verified_artifact_handoff() -> None:
    workflow = _workflow()

    assert "Build and verify Soulmate Python distributions" in workflow
    assert "Upload exact verified distributions" in workflow
    assert "soulmate-python-dists-${{ github.sha }}" in workflow
    assert "Download exact verified distributions" in workflow
    assert "Verify downloaded distributions again" in workflow
    assert "scripts/build_soulmate.py" in workflow
    assert "scripts/verify_soulmate_package.py" in workflow
    assert "needs:" in workflow
    assert "publication-gate" in workflow


def test_oidc_is_scoped_to_testpypi_publish_job() -> None:
    workflow = _workflow()

    assert workflow.count("id-token: write") == 1
    assert "name: testpypi" in workflow
    assert "url: https://test.pypi.org/p/soulmate-ai" in workflow
    assert "repository-url: https://test.pypi.org/legacy/" in workflow
    assert f"pypa/gh-action-pypi-publish@{PUBLISH_ACTION_SHA}" in workflow
    assert "# v1.14.2" in workflow
    assert "SOULMATE_PUBLICATION_ENABLED" in workflow
    assert 'PUBLICATION_TARGET" = "testpypi"' in workflow


def test_oidc_workflow_has_no_long_lived_registry_credentials() -> None:
    workflow = _workflow().lower()

    for forbidden in (
        "pypi_token",
        "test_pypi_token",
        "password:",
        "username:",
        "twine",
    ):
        assert forbidden not in workflow


def test_private_package_metadata_blocks_publication() -> None:
    workflow = _workflow()

    assert "Private :: Do Not Upload" in workflow
    assert "still marked Private :: Do Not Upload" in workflow
    assert "publication-gate" in workflow


def test_existing_manual_release_workflow_remains_non_registry_publishing() -> None:
    workflow = MANUAL_WORKFLOW.read_text(encoding="utf-8").lower()

    assert "pypi" not in workflow
    assert "twine" not in workflow
    assert "publish-github-release" in workflow
    assert "publish_release" in workflow
