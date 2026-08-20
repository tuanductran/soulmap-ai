from __future__ import annotations

import json
from pathlib import Path

import pytest

from soulmap.web import build, server
from soulmap.web.server import export_static


def test_source_fingerprint_changes_when_input_bytes_change(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("one\n", encoding="utf-8")
    first = build.source_fingerprint(tmp_path, (source,))

    source.write_text("two\n", encoding="utf-8")

    assert build.source_fingerprint(tmp_path, (source,)) != first


def test_load_reusable_output_rejects_manifest_path_escape(tmp_path: Path) -> None:
    output = tmp_path / "site"
    cache = tmp_path / "cache"
    output.mkdir()
    cache.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("do not reuse", encoding="utf-8")
    key = build.BuildKey("fingerprint", "/soulmap-ai")
    (cache / build.MANIFEST_FILENAME).write_text(
        json.dumps(
            {
                "version": build.MANIFEST_VERSION,
                "key": key.as_dict(),
                "files": ["../outside.txt"],
            }
        ),
        encoding="utf-8",
    )

    assert build.load_reusable_output(cache, output, key) is None


def test_web_cli_forwards_incremental_export_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: dict[str, object] = {}

    def fake_export(
        output: Path,
        base_path: str,
        *,
        incremental: bool,
        cache_dir: Path | None,
    ) -> list[Path]:
        calls.update(
            output=output,
            base_path=base_path,
            incremental=incremental,
            cache_dir=cache_dir,
        )
        return [output / "index.html"]

    monkeypatch.setattr(server, "export_static", fake_export)

    assert (
        server.main(
            [
                "--export-static",
                "--output",
                str(tmp_path / "site"),
                "--base-path",
                "/soulmap-ai",
                "--incremental",
                "--cache-dir",
                str(tmp_path / "cache"),
            ]
        )
        == 0
    )
    assert calls == {
        "output": tmp_path / "site",
        "base_path": "/soulmap-ai",
        "incremental": True,
        "cache_dir": tmp_path / "cache",
    }


def test_incremental_export_reuses_verified_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "site"
    cache = tmp_path / "cache"
    first = export_static(output, "/soulmap-ai", incremental=True, cache_dir=cache)
    manifest = cache / build.MANIFEST_FILENAME

    assert manifest.is_file()
    assert len(first) > 50

    monkeypatch.setattr(
        "soulmap.web.server._pages",
        lambda: pytest.fail("incremental export rendered pages again"),
    )
    second = export_static(output, "/soulmap-ai", incremental=True, cache_dir=cache)

    assert set(second) == set(first)
