from __future__ import annotations

import json
from pathlib import Path

import pytest

from web import build, server
from web.server import export_static


def test_source_fingerprint_changes_when_input_bytes_change(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("one\n", encoding="utf-8")
    first = build.source_fingerprint(tmp_path, (source,))

    source.write_text("two\n", encoding="utf-8")

    assert build.source_fingerprint(tmp_path, (source,)) != first


def test_repository_root_falls_back_to_current_working_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    real_path = Path

    class PathShim:
        def __new__(cls, value: str) -> Path:
            assert cls is PathShim
            if value == str(build.__file__):
                return real_path(tmp_path / "module.py")
            return real_path(value)

        @staticmethod
        def cwd() -> Path:
            return tmp_path

    monkeypatch.setattr(build, "Path", PathShim)

    assert build.repository_root() == tmp_path.resolve()


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


@pytest.mark.parametrize(
    "manifest",
    [
        "not-json",
        {"version": 0},
        {"version": build.MANIFEST_VERSION, "key": {}, "files": []},
        {
            "version": build.MANIFEST_VERSION,
            "key": build.BuildKey("fingerprint", "/soulmap-ai").as_dict(),
            "files": {},
        },
        {
            "version": build.MANIFEST_VERSION,
            "key": build.BuildKey("fingerprint", "/soulmap-ai").as_dict(),
            "files": [1],
        },
        {
            "version": build.MANIFEST_VERSION,
            "key": build.BuildKey("fingerprint", "/soulmap-ai").as_dict(),
            "files": ["missing.txt"],
        },
    ],
)
def test_load_reusable_output_rejects_invalid_manifests(
    tmp_path: Path, manifest: object
) -> None:
    output = tmp_path / "site"
    cache = tmp_path / "cache"
    output.mkdir()
    cache.mkdir()
    key = build.BuildKey("fingerprint", "/soulmap-ai")
    raw = manifest if isinstance(manifest, str) else json.dumps(manifest)
    (cache / build.MANIFEST_FILENAME).write_text(raw, encoding="utf-8")

    assert build.load_reusable_output(cache, output, key) is None


def test_build_inputs_tracks_peer_web_package(tmp_path: Path) -> None:
    current = tmp_path / "src" / "web" / "site.html"
    current.parent.mkdir(parents=True)
    current.write_text("current", encoding="utf-8")
    stale = tmp_path / "src" / "soulmap" / "web" / "site.html"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale", encoding="utf-8")

    inputs = build.build_inputs(tmp_path)

    assert current in inputs
    assert stale not in inputs


def test_iter_files_filters_missing_roots_and_generated_python_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "valid.txt").write_text("valid", encoding="utf-8")
    (source / "ignored.pyc").write_bytes(b"ignored")
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "cached.py").write_text("ignored", encoding="utf-8")

    assert build._iter_files(tmp_path / "missing") == []
    assert build._iter_files(source) == [source / "valid.txt"]
    assert build.build_inputs(tmp_path) == ()


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
        "web.server._pages",
        lambda: pytest.fail("incremental export rendered pages again"),
    )
    second = export_static(output, "/soulmap-ai", incremental=True, cache_dir=cache)

    assert set(second) == set(first)
