"""Contracts for the initial Soulmate library boundary."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge import keyword_lists as soulmap_keyword_lists
from soulmate.contracts import ResourceContractError, ResourceReference
from soulmate.data import parse_json_object, parse_json_value, require_str_field
from soulmate.knowledge import extract_keyword_section, load_keyword_section
from soulmate.text import normalize_text

SOULMATE_ROOT = REPO_ROOT / "src/soulmate"


def _soulmate_python_files() -> list[Path]:
    return sorted(SOULMATE_ROOT.rglob("*.py"))


def test_soulmate_package_is_importable_without_soulmap_runtime() -> None:
    import soulmate

    assert soulmate.__all__ == ()
    assert SOULMATE_ROOT.is_dir()


def test_soulmate_source_has_no_reverse_import_to_soulmap() -> None:
    for path in _soulmate_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        assert all(
            module != "soulmap" and not module.startswith("soulmap.")
            for module in imported_modules
        ), f"Soulmate must not import SoulMap: {path}"


def test_soulmate_contract_rejects_invalid_resource_references() -> None:
    with pytest.raises(ResourceContractError, match="must not be empty"):
        ResourceReference("", Path("skills/example.md"))

    with pytest.raises(ResourceContractError, match="repository-relative"):
        ResourceReference("example", Path.cwd() / "tmp" / "example.md")


def test_soulmap_wheel_includes_the_soulmate_foundation() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'packages = ["src/soulmap", "src/soulmate", "src/web"]' in pyproject


def test_soulmate_json_utilities_are_framework_neutral() -> None:
    assert parse_json_object('{"message": "hello"}') == {"message": "hello"}
    assert parse_json_value('[1, "two"]') == [1, "two"]
    assert require_str_field({"locale": "en"}, "locale") == "en"


def test_soulmap_text_api_delegates_to_soulmate() -> None:
    from soulmap.runtime.io.text_normalization import normalize_message_text

    sample = "  Don\u2019t   panic`  "
    assert normalize_message_text(sample) == normalize_text(sample)
    assert normalize_message_text(sample, strip=False) == normalize_text(
        sample, strip=False
    )


def test_soulmap_keyword_imports_delegate_to_soulmate(tmp_path: Path) -> None:
    markdown = """## Detection signals

    - \"First phrase\"
    - \"Second phrase\"

    ## Other section
    """
    path = tmp_path / "signals.md"
    path.write_text(markdown, encoding="utf-8")

    assert soulmap_keyword_lists.extract_keyword_section is extract_keyword_section
    assert soulmap_keyword_lists.load_keyword_section is load_keyword_section
    assert load_keyword_section(path, "Detection signals") == (
        "first phrase",
        "second phrase",
    )
