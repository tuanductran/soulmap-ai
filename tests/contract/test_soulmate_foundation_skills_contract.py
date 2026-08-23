from __future__ import annotations

import json

from soulmap.devtools.support.repo import REPO_ROOT

SKILLS_ROOT = REPO_ROOT / "packages" / "soulmate" / "skills"
FOUNDATION_ROOT = SKILLS_ROOT / "foundation"
MANIFEST_PATH = SKILLS_ROOT / "manifest.json"
EXPECTED_FILES = {
    "contracts.md",
    "resource-boundaries.md",
    "knowledge-resolution.md",
    "text-normalization.md",
    "data-validation.md",
    "lifecycle.md",
    "skill-manifest.md",
    "composition-and-consumers.md",
    "compatibility-and-versioning.md",
    "artifact-provenance.md",
    "determinism-and-reproducibility.md",
}
SOULMAP_COMPATIBLE_SOURCES = {
    "foundation/contracts.md",
    "foundation/resource-boundaries.md",
    "foundation/knowledge-resolution.md",
    "foundation/text-normalization.md",
    "foundation/data-validation.md",
}


def test_foundation_skill_set_has_exact_p0_p1_p2_entries() -> None:
    assert {path.name for path in FOUNDATION_ROOT.glob("*.md")} == EXPECTED_FILES


def test_foundation_manifest_matches_canonical_markdown() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "1.0"
    assert manifest["library_id"] == "soulmate-ai"
    assert manifest["distribution"]["public_registry"] is False

    entries = manifest["entries"]
    foundation_entries = [
        entry for entry in entries if entry["source"].startswith("foundation/")
    ]
    assert len(foundation_entries) == len(EXPECTED_FILES)
    assert {entry["source"] for entry in foundation_entries} == {
        f"foundation/{filename}" for filename in EXPECTED_FILES
    }
    assert len({entry["id"] for entry in foundation_entries}) == len(foundation_entries)

    for entry in foundation_entries:
        assert entry["owner"] == "Soulmate"
        assert entry["kind"] == "foundation"
        expected_consumers = (
            ["soulmate-only", "soulmap-compatible"]
            if entry["source"] in SOULMAP_COMPATIBLE_SOURCES
            else ["soulmate-only"]
        )
        assert entry["consumers"] == expected_consumers
        assert entry["artifact"] == "soulmate-ai"
        assert (SKILLS_ROOT / entry["source"]).is_file()


def test_foundation_skill_files_use_neutral_skill_front_matter() -> None:
    for path in sorted(FOUNDATION_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert 'license: "MIT"' in text
        assert "# " in text
        assert "SoulMap-specific response frameworks" not in text
