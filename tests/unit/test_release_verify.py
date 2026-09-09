"""Tests for release artifact and integration verification contracts."""

from pathlib import Path

import pytest

from soulmap.devtools.packaging.release_verify import (
    INTEGRATION_GUIDES,
    ReleaseVerificationError,
    _verify_integrations,
)


def _write_guides(root: Path, *, version: str = "0.11.0") -> None:
    guide_dir = root / "docs" / "integrations"
    guide_dir.mkdir(parents=True)
    front_matter = (
        f'---\ndoctrine_source: "SOULMAP.md"\nsoulmap_version: "{version}"\n---\n\n'
    )
    for relative_path in INTEGRATION_GUIDES:
        path = root / relative_path
        path.write_text(front_matter + "# Guide\n", encoding="utf-8")


def test_verify_integrations_accepts_all_supported_guides(tmp_path: Path) -> None:
    _write_guides(tmp_path)

    results = _verify_integrations(tmp_path, "0.11.0")

    assert len(results) == 4
    assert all(result["doctrine_source"] == "SOULMAP.md" for result in results)
    assert all(result["soulmap_version"] == "0.11.0" for result in results)


def test_verify_integrations_rejects_version_drift(tmp_path: Path) -> None:
    _write_guides(tmp_path, version="0.10.0")

    with pytest.raises(
        ReleaseVerificationError,
        match=r"soulmap_version must be 0\.11\.0, got 0\.10\.0",
    ):
        _verify_integrations(tmp_path, "0.11.0")


def test_verify_integrations_rejects_doctrine_source_drift(tmp_path: Path) -> None:
    _write_guides(tmp_path)
    path = tmp_path / INTEGRATION_GUIDES[0]
    path.write_text(
        path.read_text(encoding="utf-8").replace("SOULMAP.md", "other.md"),
        encoding="utf-8",
    )

    with pytest.raises(
        ReleaseVerificationError,
        match=r"doctrine_source must be SOULMAP\.md, got other\.md",
    ):
        _verify_integrations(tmp_path, "0.11.0")


def test_verify_integrations_rejects_missing_guide(tmp_path: Path) -> None:
    _write_guides(tmp_path)
    (tmp_path / INTEGRATION_GUIDES[-1]).unlink()

    with pytest.raises(ReleaseVerificationError, match="integration guide is missing"):
        _verify_integrations(tmp_path, "0.11.0")
