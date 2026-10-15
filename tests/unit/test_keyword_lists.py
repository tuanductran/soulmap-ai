from pathlib import Path
from typing import Any

import pytest

from soulmap.runtime.knowledge.keyword_lists import (
    _read_markdown_text_cached,
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
        self: Path, *args: Any, **kwargs: Any
    ) -> str:
        nonlocal reads
        if self.resolve() == path.resolve():
            reads += 1
        return original_read_text(self, *args, **kwargs)

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
