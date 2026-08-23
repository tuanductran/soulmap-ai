from __future__ import annotations

from pathlib import Path

from soulmap.cli import _command_table
from soulmap.devtools.packaging import catalog_parity
from soulmap.devtools.support.repo import REPO_ROOT


def test_catalog_parity_matches_checked_in_sources() -> None:
    assert catalog_parity.verify_catalog_parity(REPO_ROOT) == []


def test_catalog_parity_reports_library_only_entry(monkeypatch) -> None:
    monkeypatch.setattr(
        catalog_parity,
        "CATALOG",
        tuple(entry for entry in catalog_parity.CATALOG if entry.slug != "voice"),
    )

    errors = catalog_parity.verify_catalog_parity(REPO_ROOT)

    assert errors == ["Library entry has no public catalog slug: voice"]


def test_catalog_parity_is_a_public_maintainer_command() -> None:
    assert "catalog-parity" in _command_table()


def test_catalog_parity_does_not_change_repo_root_resolution() -> None:
    assert Path(REPO_ROOT / "library/catalog.json").is_file()
