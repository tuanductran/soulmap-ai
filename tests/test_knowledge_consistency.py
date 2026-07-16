from pathlib import Path

from soulmap.runtime.knowledge.consistency import (
    find_config_usage,
    find_python_markdown_duplicates,
)


def test_find_python_markdown_duplicates(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "patterns.py").write_text(
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
    assert duplicates[0].python_path == config / "patterns.py"
    assert duplicates[0].markdown_path == skills / "example.md"
    assert duplicates[0].markdown_section == "Detection signals"
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
        '- "want to die" or "want to end my life"\n',
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
    (config / "patterns.py").write_text(
        'SIGNALS: tuple[str, ...] = ("framework phrase",)\n',
        encoding="utf-8",
    )

    frameworks = tmp_path / "frameworks"
    frameworks.mkdir()
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
    (config / "patterns.py").write_text(
        'SIGNALS: tuple[str, ...] = ("pattern phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills/frameworks"
    skills.mkdir(parents=True)
    (skills / "pattern-mapper.md").write_text(
        "## Pattern 1: Example pattern\n\n"
        "**Detection signals:**\n\n"
        '- "pattern phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert duplicates[0].source_kind == "pattern_framework"
    assert duplicates[0].classification == "knowledge_duplicate"


def test_activation_signals_use_runtime_keyword_parser(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "patterns.py").write_text(
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
    (config / "patterns.py").write_text(
        'SIGNALS: tuple[str, ...] = ("shared phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir()
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
    (config / "patterns.py").write_text(
        'ACTIVE: tuple[str, ...] = ("active",)\n'
        'ORPHANED: tuple[str, ...] = ("orphaned",)\n',
        encoding="utf-8",
    )

    detector = tmp_path / "src/soulmap/runtime/detectors"
    detector.mkdir(parents=True)
    (detector / "example.py").write_text(
        "from soulmap.runtime.config.patterns import ACTIVE\n\n"
        "VALUE = ACTIVE\n",
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)
    by_constant = {item.constant: item for item in usage}

    assert not by_constant["ACTIVE"].is_orphaned
    assert by_constant["ACTIVE"].referenced_from == (detector / "example.py",)
    assert by_constant["ORPHANED"].is_orphaned


def test_config_exports_are_not_runtime_usage(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "patterns.py").write_text(
        'SIGNALS: tuple[str, ...] = ("signal",)\n',
        encoding="utf-8",
    )
    (config / "__init__.py").write_text(
        "from .patterns import SIGNALS\n\n__all__ = [\"SIGNALS\"]\n",
        encoding="utf-8",
    )

    usage = find_config_usage(tmp_path)

    assert usage[0].is_orphaned


def test_safety_overlap_is_classified_as_protected(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "safety.py").write_text(
        'CRISIS_TIER1: tuple[str, ...] = ("protected phrase",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir()
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
    skills.mkdir()
    (skills / "safety.md").write_text(
        '## Detection signals\n\nSignals:\n\n- "grandiosity phrase"\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert duplicates[0].classification == "review_required"


def test_find_python_markdown_duplicates_is_diagnostic_only(tmp_path: Path) -> None:
    config = tmp_path / "src/soulmap/runtime/config"
    config.mkdir(parents=True)
    (config / "patterns.py").write_text(
        'SIGNALS: tuple[str, ...] = ("python only",)\n',
        encoding="utf-8",
    )

    skills = tmp_path / "skills"
    skills.mkdir()
    (skills / "example.md").write_text(
        '## Detection signals\n\nSignals:\n\n- "markdown only"\n',
        encoding="utf-8",
    )

    assert find_python_markdown_duplicates(tmp_path) == ()
