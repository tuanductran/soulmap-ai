"""Contracts for the SoulMap -> Soulmate dependency direction."""

from __future__ import annotations

from pathlib import Path

from soulmap.cli import _command_table
from soulmap.devtools.checks.dependency_direction import check_source_tree
from soulmap.devtools.support.repo import REPO_ROOT


def _write_source(root: Path, package: str, filename: str, content: str) -> None:
    path = root / "src" / package / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_repository_dependency_direction_is_clean() -> None:
    assert check_source_tree(REPO_ROOT) == []


def test_soulmate_reverse_import_is_rejected(tmp_path: Path) -> None:
    _write_source(
        tmp_path,
        "soulmate",
        "bad.py",
        "from soulmap.runtime.routing import framework_selector\n",
    )

    issues = check_source_tree(tmp_path)

    assert len(issues) == 1
    assert issues[0].message == (
        "Soulmate must not import SoulMap (soulmap.runtime.routing)"
    )


def test_soulmap_private_soulmate_module_is_rejected(tmp_path: Path) -> None:
    _write_source(
        tmp_path,
        "soulmap",
        "bad.py",
        "from soulmate.data.json import parse_json_object\n",
    )

    issues = check_source_tree(tmp_path)

    assert len(issues) == 1
    assert issues[0].message == (
        "SoulMap must import Soulmate through a public namespace; "
        "got soulmate.data.json"
    )


def test_checker_is_registered_as_a_cli_command() -> None:
    assert "check-dependencies" in _command_table()
