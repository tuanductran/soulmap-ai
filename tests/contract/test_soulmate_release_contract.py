"""Contracts for the isolated Soulmate release preparation workflow."""

from __future__ import annotations

import tomllib

from soulmap.devtools.support.repo import REPO_ROOT

PACKAGE_ROOT = REPO_ROOT / "packages" / "soulmate"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "soulmate-release.yml"


def test_soulmate_manifest_has_an_independent_package_identity() -> None:
    manifest = tomllib.loads(
        (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = manifest["project"]

    assert project["name"] == "soulmate-ai"
    assert project["version"] == "0.1.0"
    assert project["dependencies"] == []
    assert manifest["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == [
        "src/soulmate"
    ]


def test_soulmate_package_metadata_is_complete() -> None:
    assert (PACKAGE_ROOT / "README.md").is_file()
    assert (PACKAGE_ROOT / "LICENSE").is_file()
    assert not (PACKAGE_ROOT / "src").exists()

    builder = (REPO_ROOT / "scripts" / "build_soulmate.py").read_text(encoding="utf-8")
    assert 'REPO_ROOT / "src" / "soulmate"' in builder


def test_soulmate_workflow_has_manual_publish_gate() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "publish_release:" in workflow
    assert "default: false" in workflow
    assert "scripts/build_soulmate.py" in workflow
    assert "scripts/verify_soulmate_package.py" in workflow
    assert 'gh release create "soulmate-v${SOULMATE_VERSION}"' in workflow
    assert "if: inputs.publish_release == true" in workflow
    assert "pypi" not in workflow.lower()
    assert "twine" not in workflow.lower()


def test_workflow_targets_the_checked_out_commit() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert '--target "${GITHUB_SHA}"' in workflow
