from __future__ import annotations

import ast
from pathlib import Path

from scripts.audit_python_reachability import (
    DEFAULT_ENTRY_MODULES,
    analyze,
    module_name,
    resolve_imports,
)


def test_default_entries_cover_cli_action_and_governance_entrypoints() -> None:
    assert DEFAULT_ENTRY_MODULES == (
        "soulmap.cli",
        "action.__main__",
        "soulmap.devtools.checks.p_level_governance",
    )


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
        "import importlib\n"
        "importlib.import_module('soulmap.dynamic')\n"
        "__import__('soulmap.other')\n"
        "from importlib import import_module\n"
        "import_module('soulmap.third')\n"
        "importlib.import_module(module_name)\n"
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


def test_resolve_imports_uses_package_name_for_relative_import_in_init() -> None:
    tree = ast.parse("from .helper import VALUE")
    found = resolve_imports(
        tree,
        "pkg.sub",
        {"pkg", "pkg.sub", "pkg.sub.helper", "pkg.helper"},
        is_package=True,
    )
    assert found == {"pkg.sub.helper"}


def test_resolve_imports_ignores_relative_imports_beyond_top_level() -> None:
    tree = ast.parse("from ...helper import VALUE")
    found = resolve_imports(
        tree,
        "pkg.sub.module",
        {"pkg", "pkg.sub", "pkg.helper"},
    )
    assert found == set()


def test_analyze_tracks_relative_imports_from_package_initializer(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src" / "pkg"
    subpackage = source / "sub"
    subpackage.mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "cli.py").write_text("import pkg.sub\n", encoding="utf-8")
    (subpackage / "__init__.py").write_text(
        "from .helper import VALUE\n", encoding="utf-8"
    )
    (subpackage / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")

    reachable, candidates, missing = analyze(tmp_path, ("pkg.cli",))

    assert "pkg.sub.helper" in reachable
    assert candidates == set()
    assert missing == []


def test_candidate_directories_require_every_module_to_be_unreachable(
    tmp_path: Path,
) -> None:
    from scripts.audit_python_reachability import candidate_directories

    source = tmp_path / "src"
    unused = source / "pkg" / "unused"
    used = source / "pkg" / "used"
    unused.mkdir(parents=True)
    used.mkdir(parents=True)
    (unused / "__init__.py").write_text("", encoding="utf-8")
    (unused / "first.py").write_text("VALUE = 1\\n", encoding="utf-8")
    (unused / "second.py").write_text("VALUE = 2\\n", encoding="utf-8")
    (used / "__init__.py").write_text("", encoding="utf-8")
    (used / "entry.py").write_text("VALUE = 3\\n", encoding="utf-8")

    candidates = {
        "pkg.unused",
        "pkg.unused.first",
        "pkg.unused.second",
    }

    assert candidate_directories(tmp_path, candidates) == ("src/pkg/unused",)


def test_candidate_directories_do_not_flag_mixed_reachability_packages(
    tmp_path: Path,
) -> None:
    from scripts.audit_python_reachability import candidate_directories

    package = tmp_path / "src" / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "used.py").write_text("VALUE = 1\\n", encoding="utf-8")
    (package / "maybe_unused.py").write_text("VALUE = 2\\n", encoding="utf-8")

    assert candidate_directories(tmp_path, {"pkg.maybe_unused"}) == ()
