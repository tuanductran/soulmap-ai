from __future__ import annotations

import ast
from pathlib import Path

from scripts.audit_python_reachability import analyze, module_name, resolve_imports


def test_module_name_maps_package_and_module_paths() -> None:
    source_root = Path("src")
    package_init = source_root / "soulmap" / "__init__.py"
    assert module_name(package_init, source_root) == "soulmap"
    assert module_name(source_root / "soulmap" / "cli.py", source_root) == "soulmap.cli"


def test_resolve_imports_only_returns_known_local_modules() -> None:
    tree = ast.parse("import soulmap.cli\nimport requests\nfrom soulmap import runtime")
    found = resolve_imports(
        tree,
        "soulmap.devtools.example",
        {"soulmap", "soulmap.cli", "soulmap.runtime"},
    )
    assert found == {"soulmap", "soulmap.cli", "soulmap.runtime"}


def test_analyze_reports_unreachable_as_candidates_not_deletions(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src" / "soulmap"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "cli.py").write_text("import soulmap.used\n", encoding="utf-8")
    (source / "used.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "dynamic.py").write_text("VALUE = 2\n", encoding="utf-8")

    reachable, candidates, missing = analyze(tmp_path, ("soulmap.cli",))

    assert reachable == {"soulmap", "soulmap.cli", "soulmap.used"}
    assert candidates == {"soulmap.dynamic"}
    assert missing == []


def test_resolve_imports_tracks_literal_dynamic_imports() -> None:
    tree = ast.parse(
        "import importlib\\n"
        "importlib.import_module('soulmap.dynamic')\\n"
        "__import__('soulmap.other')\\n"
        "from importlib import import_module\\n"
        "import_module('soulmap.third')\\n"
        "importlib.import_module(module_name)\\n"
    )
    found = resolve_imports(
        tree,
        "soulmap.cli",
        {
            "soulmap",
            "soulmap.dynamic",
            "soulmap.other",
            "soulmap.third",
        },
    )
    assert found == {
        "soulmap.dynamic",
        "soulmap.other",
        "soulmap.third",
    }
