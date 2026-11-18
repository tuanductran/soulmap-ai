import os
from pathlib import Path

import pytest

from soulmap.runtime.knowledge.keyword_lists import (
    _read_markdown_text_cached,
    extract_keyword_section,
    extract_labeled_groups,
    extract_table_rows,
    load_key_value_table,
    load_keyword_section,
)


def test_loaders_read_each_markdown_version_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "knowledge.md"
    path.write_text(
        '## Detection signals\n\n- "first phrase"\n\n'
        "## Scoring\n\n| Rule | Value |\n| --- | --- |\n| Weight | 2 |\n",
        encoding="utf-8",
    )
    _read_markdown_text_cached.cache_clear()
    original_read_text = Path.read_text
    reads = 0

    def counted_read_text(
        self: Path,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> str:
        nonlocal reads
        if self.resolve() == path.resolve():
            reads += 1
        return original_read_text(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", counted_read_text)

    assert load_keyword_section(path, "Detection signals") == ("first phrase",)
    assert load_key_value_table(path, "Scoring") == {"Weight": "2"}
    assert reads == 1


def test_markdown_cache_invalidates_when_file_changes(tmp_path: Path) -> None:
    path = tmp_path / "knowledge.md"
    path.write_text('## Signals\n\n- "old phrase"\n', encoding="utf-8")
    _read_markdown_text_cached.cache_clear()

    assert load_keyword_section(path, "Signals") == ("old phrase",)

    path.write_text(
        '## Signals\n\n- "new phrase with different length"\n',
        encoding="utf-8",
    )

    assert load_keyword_section(path, "Signals") == (
        "new phrase with different length",
    )


def test_markdown_cache_invalidates_when_size_and_mtime_are_preserved(
    tmp_path: Path,
) -> None:
    path = tmp_path / "knowledge.md"
    path.write_text('## Signals\\n\\n- "old signal"\\n', encoding="utf-8")
    _read_markdown_text_cached.cache_clear()
    original_stat = path.stat()

    assert load_keyword_section(path, "Signals") == ("old signal",)

    path.write_text('## Signals\\n\\n- "new signal"\\n', encoding="utf-8")
    os.utime(path, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))

    assert path.stat().st_size == original_stat.st_size
    assert path.stat().st_mtime_ns == original_stat.st_mtime_ns
    assert load_keyword_section(path, "Signals") == ("new signal",)


def test_section_extractors_share_heading_boundaries() -> None:
    signals = (
        "## Root\n\n"
        "### Detection signals\n\n"
        "Active anger:\n\n"
        '- "inside phrase"\n\n'
        "#### Supporting detail\n\n"
        '- "nested phrase"\n\n'
        "### Later section\n\n"
        '- "outside phrase"\n'
    )

    assert extract_keyword_section(signals, "Detection signals") == (
        "inside phrase",
        "nested phrase",
    )
    assert extract_labeled_groups(signals, "Detection signals") == {
        "active anger": ("inside phrase", "nested phrase")
    }

    table = (
        "## Contracts\n\n"
        "### Scoring\n\n"
        "| Rule | Value |\n"
        "| --- | --- |\n"
        "| Weight | 2 |\n\n"
        "### Other\n\n"
        "| Ignore | 3 |\n"
    )
    assert extract_table_rows(table, "Scoring") == (("Weight", "2"),)
