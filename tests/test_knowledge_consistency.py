from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge.consistency import (
    find_config_usage,
    find_python_markdown_duplicates,
    markdown_consumers,
)


def test_find_python_markdown_duplicates(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("shared phrase", "python only")\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills/frameworks"
    skills.mkdir(parents=True)
    (skills / "example.md").write_text(
        '## Detection signals\n\nSignal group:\n\n- "shared phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert len(duplicates) == 1
    assert duplicates[0].phrase == "shared phrase"
    assert duplicates[0].constant == "SIGNALS"
    assert duplicates[0].python_path == config / "meaning.py"
    assert duplicates[0].markdown_path == skills / "example.md"
    assert duplicates[0].markdown_section == "Detection signals"
    assert duplicates[0].markdown_group == "signal group"
    assert duplicates[0].source_kind == "markdown"
    assert duplicates[0].classification == "knowledge_duplicate"


def test_find_python_markdown_duplicates_extracts_multiple_signal_units(
    tmp_path: Path,
) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "safety.py").write_text(
        'CRISIS_TIER1: tuple[str, ...] = ("want to die", "want to end my life")\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "safety.md").write_text(
        "## Detection signals\n\nCrisis signals:\n\n"
        '- "want to die"\n'
        '- "want to end my life"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert {duplicate.phrase for duplicate in duplicates} == {
        "want to die",
        "want to end my life",
    }
    assert len(duplicates) == 2


def test_find_python_markdown_duplicates_scans_framework_root(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("framework phrase",)\n',
        encoding="utf-8",
    )

    frameworks = tmp_path / "frameworks"
    frameworks.mkdir(parents=True)
    (frameworks / "example.md").write_text(
        '## Detection signals\n\nSignal group:\n\n- "framework phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert len(duplicates) == 1
    assert duplicates[0].markdown_section == "Detection signals"


def test_pattern_mapper_is_classified_as_structured_framework(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("pattern phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills/frameworks"
    skills.mkdir(parents=True)
    (skills / "pattern-mapper.md").write_text(
        '## Pattern 1: Example pattern\n\n**Detection signals:**\n\n- "pattern phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert duplicates[0].source_kind == "pattern_framework"
    assert duplicates[0].classification == "knowledge_duplicate"


def test_activation_signals_use_runtime_keyword_parser(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("activation phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills/frameworks"
    skills.mkdir(parents=True)
    (skills / "example.md").write_text(
        '## Activation Signals\n\n- "activation phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert len(duplicates) == 1
    assert duplicates[0].markdown_section == "Activation Signals"


def test_non_signal_sections_are_not_treated_as_knowledge(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("shared phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir(parents=True)
    (skills / "example.md").write_text(
        '## Tone rules\n\n- "shared phrase"\n',
        encoding="utf-8",
    )

    assert find_python_markdown_duplicates(tmp_path) == ()


def test_find_config_usage_distinguishes_active_and_orphaned_constants(
    tmp_path: Path,
) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'ACTIVE: tuple[str, ...] = ("active",)\n'
        'ORPHANED: tuple[str, ...] = ("orphaned",)\n',
        encoding="utf-8",
    )

    detector = tmp_path / "src/soulmap/runtime/detectors"
    detector.mkdir(parents=True)
    (detector / "example.py").write_text(
        "from soulmap.runtime.config.meaning import ACTIVE\n\nVALUE = ACTIVE\n",
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)
    by_constant = {item.constant: item for item in usage}

    assert not by_constant["ACTIVE"].is_orphaned
    assert by_constant["ACTIVE"].referenced_from == (detector / "example.py",)
    assert by_constant["ORPHANED"].is_orphaned


def test_find_config_usage_ignores_same_name_local_variable(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'ACTIVE: tuple[str, ...] = ("active",)\n',
        encoding="utf-8",
    )

    detector = tmp_path / "src/soulmap/runtime/detectors"
    detector.mkdir(parents=True)
    (detector / "example.py").write_text(
        'ACTIVE = load_keyword_section("Activation Signals")\nVALUE = ACTIVE\n',
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)

    assert usage[0].is_orphaned


def test_find_config_usage_tracks_config_module_alias(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'ACTIVE: tuple[str, ...] = ("active",)\n',
        encoding="utf-8",
    )

    detector = tmp_path / "src/soulmap/runtime/detectors"
    detector.mkdir(parents=True)
    (detector / "example.py").write_text(
        "import soulmap.runtime.config.meaning as meaning\n\nVALUE = meaning.ACTIVE\n",
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)

    assert not usage[0].is_orphaned
    assert usage[0].referenced_from == (detector / "example.py",)


def test_config_exports_are_not_runtime_usage(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("signal",)\n',
        encoding="utf-8",
    )
    (config / "__init__.py").write_text(
        'from .patterns import SIGNALS\n\n__all__ = ["SIGNALS"]\n',
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)

    assert len(usage) == 1
    assert usage[0].is_orphaned


def test_safety_overlap_is_classified_as_protected(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "safety.py").write_text(
        'CRISIS_TIER1: tuple[str, ...] = ("protected phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir(parents=True)
    (skills / "safety.md").write_text(
        '## Detection signals\n\nCrisis signals:\n\n- "protected phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert duplicates[0].classification == "safety_protected_overlap"


def test_grandiosity_overlap_requires_review(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "safety.py").write_text(
        'GRANDIOSITY_SIGNALS: tuple[str, ...] = ("grandiosity phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir(parents=True)
    (skills / "safety.md").write_text(
        '## Detection signals\n\nSignals:\n\n- "grandiosity phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert duplicates[0].classification == "review_required"


def test_find_python_markdown_duplicates_is_diagnostic_only(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "meaning.py").write_text(
        'SIGNALS: tuple[str, ...] = ("python only",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir(parents=True)
    (skills / "example.md").write_text(
        '## Detection signals\n\nSignals:\n\n- "markdown only"\n',
        encoding="utf-8",
    )

    assert find_python_markdown_duplicates(tmp_path) == ()


def test_find_config_usage_tracks_package_level_reexport_import(
    tmp_path: Path,
) -> None:
    """Regression test for Issue #126.

    A detector that imports a constant via the config *package*
    (``from soulmap.runtime.config import X``, relying on ``__init__.py`` to
    re-export it) must be recognized as a real reference, not a false
    orphan. Before the fix, the symbol table only had entries keyed by each
    submodule's own module name (e.g. ``...config.safety``), never by the
    plain package name (``...config``) that this import style resolves to.
    """
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "safety.py").write_text(
        'CRISIS_TIER1: tuple[str, ...] = ("want to die",)\n',
        encoding="utf-8",
    )
    (config / "__init__.py").write_text(
        'from .safety import CRISIS_TIER1\n\n__all__ = ["CRISIS_TIER1"]\n',
        encoding="utf-8",
    )

    detector = tmp_path / "src/soulmap/runtime/detectors"
    detector.mkdir(parents=True)
    (detector / "crisis_detector.py").write_text(
        "from soulmap.runtime.config import CRISIS_TIER1\n\nVALUE = CRISIS_TIER1\n",
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)
    by_constant = {item.constant: item for item in usage}

    assert not by_constant["CRISIS_TIER1"].is_orphaned
    assert by_constant["CRISIS_TIER1"].referenced_from == (
        detector / "crisis_detector.py",
    )


def test_find_config_usage_package_reexport_requires_actual_import(
    tmp_path: Path,
) -> None:
    """A name only defined in a submodule, and never imported by
    ``__init__.py``, must not resolve via the package name -- the package
    genuinely does not export it, so a hypothetical
    ``from soulmap.runtime.config import X`` would fail at runtime too."""
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "safety.py").write_text(
        'NOT_REEXPORTED: tuple[str, ...] = ("phrase",)\n',
        encoding="utf-8",
    )
    (config / "__init__.py").write_text("", encoding="utf-8")

    usage = find_config_usage(tmp_path)

    assert usage[0].constant == "NOT_REEXPORTED"
    assert usage[0].is_orphaned


def test_real_repository_crisis_constants_are_not_orphaned() -> None:
    """End-to-end regression guard for Issue #126 against the real repo.

    ``crisis_detector.py`` imports these via
    ``from soulmap.runtime.config import ...`` (package-level, not
    submodule-level). Before the fix this pattern was always misreported as
    orphaned regardless of actual usage.
    """
    usage = find_config_usage(REPO_ROOT)
    by_constant = {item.constant: item for item in usage}

    for constant in ("CRISIS_TIER1", "CRISIS_TIER2", "GRANDIOSITY_SIGNALS"):
        assert constant in by_constant, constant
        assert not by_constant[constant].is_orphaned, constant


def test_markdown_consumers_finds_runtime_markdown_loader(tmp_path: Path) -> None:
    markdown = tmp_path / "skills/frameworks/example.md"
    markdown.parent.mkdir(parents=True)
    markdown.write_text("## Detection signals\n", encoding="utf-8")

    detector = tmp_path / "src/soulmap/runtime/detectors/example_detector.py"
    detector.parent.mkdir(parents=True)
    detector.write_text(
        "SIGNALS = load_labeled_groups(\n"
        '    default_skill_path("skills/frameworks/example.md"), "Detection signals"\n'
        ")\n",
        encoding="utf-8",
    )

    assert markdown_consumers(tmp_path, markdown) == (detector,)
