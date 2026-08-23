from __future__ import annotations

import json
import zipfile
from collections.abc import Callable
from pathlib import Path

import pytest

from scripts.verify_soulmap_with_soulmate import _verify
from soulmap.devtools.packaging import composition
from soulmap.devtools.packaging.build_skill import build_zip

REPO_ROOT = Path(__file__).resolve().parents[2]
SCOPE_PATH = (
    REPO_ROOT
    / "src"
    / "soulmap"
    / "runtime"
    / "knowledge"
    / "soulmate_composition_scope.json"
)
MANIFEST_PATH = REPO_ROOT / "packages" / "soulmate" / "skills" / "manifest.json"


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rewrite_archive(
    source: Path,
    target: Path,
    mutate: Callable[[dict[str, bytes]], dict[str, bytes]],
) -> None:
    with zipfile.ZipFile(source) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    mutated = mutate(members)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in mutated.items():
            archive.writestr(name, content)


def test_composition_scope_matches_canonical_soulmate_manifest() -> None:
    manifest = _read_json(MANIFEST_PATH)
    scope = _read_json(SCOPE_PATH)
    manifest_entries = manifest["entries"]
    scope_entries = scope["entries"]
    assert isinstance(manifest_entries, list)
    assert isinstance(scope_entries, list)
    expected = [
        {
            "id": entry["id"],
            "version": entry["version"],
            "kind": entry["kind"],
            "source": entry["source"],
            "compatibility": entry["compatibility"],
        }
        for entry in manifest_entries
    ]
    assert scope_entries == expected
    assert len(scope_entries) == 21


def test_composed_artifacts_are_deterministic_and_verifiable(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_zip, first_skill = composition.build_all(first)
    second_zip, second_skill = composition.build_all(second)

    assert first_zip.read_bytes() == second_zip.read_bytes()
    assert first_skill.read_bytes() == second_skill.read_bytes()
    assert _verify(first_zip, include_plugin=False)["soulmate_entries"] == 21
    assert _verify(first_skill, include_plugin=True)["soulmate_entries"] == 21


def test_composed_skill_contains_framework_precedence_and_soulmate_paths(
    tmp_path: Path,
) -> None:
    _, skill_path = composition.build_all(tmp_path)
    with zipfile.ZipFile(skill_path) as archive:
        skill = archive.read("SKILL.md").decode("utf-8")
        assert (
            "This composed artifact runs the SoulMap Framework on top of the Soulmate Library."
            in skill
        )
        assert "soulmate/foundation/" in skill
        assert "soulmate/companion/" in skill
        assert "SoulMap orchestration pipeline remains authoritative" in skill
        assert "not replace the Framework" in skill


def test_composed_artifact_does_not_leak_source_only_metadata(tmp_path: Path) -> None:
    zip_path, skill_path = composition.build_all(tmp_path)
    for artifact in (zip_path, skill_path):
        with zipfile.ZipFile(artifact) as archive:
            names = set(archive.namelist())
            assert "soulmate_composition_scope.json" not in names
            assert all("packages/soulmate/skills" not in name for name in names)
            contents = b"\n".join(
                archive.read(name) for name in names if not name.endswith("/")
            )
            assert (
                b"src/soulmap/runtime/knowledge/soulmate_consumer_scope.json"
                not in contents
            )


def test_composition_scope_fails_closed_on_unknown_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _read_json(SCOPE_PATH)
    payload["unexpected"] = True
    bad_scope = tmp_path / "scope.json"
    bad_scope.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(composition, "COMPOSITION_SCOPE_PATH", bad_scope)
    with pytest.raises(composition.CompositionError, match="unknown or missing fields"):
        composition._scope_entries()


def test_verifier_rejects_unexpected_member(tmp_path: Path) -> None:
    source, _ = composition.build_all(tmp_path / "good")
    bad = tmp_path / "extra.zip"
    _rewrite_archive(source, bad, lambda members: {**members, "unexpected.txt": b"x"})
    with pytest.raises(ValueError, match="member parity failed"):
        _verify(bad, include_plugin=False)


def test_verifier_rejects_content_mutation(tmp_path: Path) -> None:
    source, _ = composition.build_all(tmp_path / "good")

    def mutate(members: dict[str, bytes]) -> dict[str, bytes]:
        members["SKILL.md"] += b"\nunauthorized mutation\n"
        return members

    bad = tmp_path / "mutated.zip"
    _rewrite_archive(source, bad, mutate)
    with pytest.raises(ValueError, match=r"byte parity failed: SKILL\.md"):
        _verify(bad, include_plugin=False)


def test_verifier_rejects_missing_member(tmp_path: Path) -> None:
    source, _ = composition.build_all(tmp_path / "good")
    bad = tmp_path / "missing.zip"

    def remove_skill(members: dict[str, bytes]) -> dict[str, bytes]:
        members.pop("SKILL.md")
        return members

    _rewrite_archive(source, bad, remove_skill)
    with pytest.raises(ValueError, match="member parity failed"):
        _verify(bad, include_plugin=False)


def test_composition_scope_rejects_unsafe_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _read_json(SCOPE_PATH)
    entries = payload["entries"]
    assert isinstance(entries, list)
    first_entry = entries[0]
    assert isinstance(first_entry, dict)
    first_entry["source"] = "../escape.md"
    bad_scope = tmp_path / "scope.json"
    bad_scope.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(composition, "COMPOSITION_SCOPE_PATH", bad_scope)
    with pytest.raises(composition.CompositionError, match="Unsafe composition source"):
        composition._scope_entries()


def test_composition_fails_when_canonical_source_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty_source = tmp_path / "empty-source"
    empty_source.mkdir()
    monkeypatch.setattr(composition, "SOULMATE_SKILLS_ROOT", empty_source)
    with pytest.raises(
        composition.CompositionError, match="Missing Soulmate skill source"
    ):
        composition._canonical_entries()


def test_composition_does_not_change_standalone_soulmap_artifact(
    tmp_path: Path,
) -> None:
    standalone = build_zip(REPO_ROOT)
    before = standalone.read_bytes()
    composition.build_all(tmp_path / "composed")
    assert standalone.read_bytes() == before
