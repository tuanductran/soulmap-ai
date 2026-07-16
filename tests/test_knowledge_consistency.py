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
        '## Detection signals\n\n- "markdown only"\n',
        encoding="utf-8",
    )

    assert find_python_markdown_duplicates(tmp_path) == ()
