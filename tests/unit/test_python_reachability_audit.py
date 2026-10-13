from __future__ import annotations

from pathlib import Path

from scripts.audit_python_reachability import analyze, module_name, resolve_imports
import ast


def test_module_name_maps_package_and_module_paths() -> None:
    source_root = Path("src")
    assert module_name(source_root / "soulmap" / "__init__.py", source_root) == "soulmap"
    assert module_name(source_root / "soulmap" / "cli.py", source_root) == "soulmap.cli"


def test_resolve_imports_only_returns_known_local_modules() -> None:
    tree = ast.parse("import soulmap.cli\nimport requests\nfrom soulmap import runtime")
    found = resolve_imports(
        tree,
        "soulmap.devtools.example",
        {"soulmap", "soulmap.cli", "soulmap.runtime"},
    )
    assert found == {"soulmap.cli", "soulmap.runtime"}


def test_analyze_reports_unreachable_as_candidates_not_deletions(tmp_path: Path) -> None:
    source = tmp_path / "src" / "soulmap"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "cli.py").write_text("import soulmap.used\n", encoding="utf-8")
    (source / "used.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "dynamic.py").write_text("VALUE = 2\n", encoding="utf-8")

    reachable, candidates, missing = analyze(tmp_path, ("soulmap.cli",))

    assert reachable == {"soulmap.cli", "soulmap.used"}
    assert candidates == {"soulmap", "soulmap.dynamic"}
    assert missing == []
