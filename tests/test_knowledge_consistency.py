from pathlib import Path

from soulmap.runtime.knowledge.consistency import (
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
        '## Detection signals\n\n- "shared phrase"\n',
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
        '## Detection signals\n\n- framework phrase\n',
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
        '## Detection signals\n\n- pattern phrase\n',
        encoding="utf-8",
    )

    duplicates = find_python_markdown_duplicates(tmp_path)

    assert duplicates[0].source_kind == "pattern_framework"
    assert duplicates[0].classification == "knowledge_duplicate"


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
        '## Signals\n\n- protected phrase\n',
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
        '## Signals\n\n- grandiosity phrase\n',
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
        '## Detection signals\n\n- markdown only\n',
        encoding="utf-8",
    )

    assert find_python_markdown_duplicates(tmp_path) == ()
