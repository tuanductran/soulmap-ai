from __future__ import annotations

import json
from typing import Any

from soulmap.devtools.support.repo import REPO_ROOT

SKILLS_ROOT = REPO_ROOT / "packages" / "soulmate" / "skills"
COMPANION_ROOT = SKILLS_ROOT / "companion"
MANIFEST_PATH = SKILLS_ROOT / "manifest.json"
EXPECTED_ORDER = (
    "identity.md",
    "presence.md",
    "reflective-listening.md",
    "emotional-attunement.md",
    "gentle-inquiry.md",
    "boundaries-and-consent.md",
    "grounded-companionship.md",
    "human-connection-bridge.md",
    "repair-and-misattunement.md",
    "session-closure.md",
)
EXPECTED_FILES = set(EXPECTED_ORDER)
EXPECTED_IDS = {
    "soulmate.companion.identity",
    "soulmate.companion.presence",
    "soulmate.companion.reflective-listening",
    "soulmate.companion.emotional-attunement",
    "soulmate.companion.gentle-inquiry",
    "soulmate.companion.boundaries-and-consent",
    "soulmate.companion.grounded-companionship",
    "soulmate.companion.human-connection-bridge",
    "soulmate.companion.repair-and-misattunement",
    "soulmate.companion.session-closure",
}


def _manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_companion_skill_set_has_exact_initial_entries() -> None:
    assert {path.name for path in COMPANION_ROOT.glob("*.md")} == EXPECTED_FILES


def test_companion_manifest_entries_are_explicit_and_soulmate_only() -> None:
    entries = [
        entry
        for entry in _manifest()["entries"]
        if entry["source"].startswith("companion/")
    ]

    assert {entry["id"] for entry in entries} == EXPECTED_IDS
    assert [entry["source"] for entry in entries] == [
        f"companion/{filename}" for filename in EXPECTED_ORDER
    ]
    assert len(entries) == len(EXPECTED_FILES)
    for entry in entries:
        assert entry["owner"] == "Soulmate"
        assert entry["kind"] == "companion"
        assert entry["consumers"] == ["soulmate-only"]
        assert entry["compatibility"] == ">=0.1.0,<0.2.0"
        assert entry["artifact"] == "soulmate-ai"
        assert (SKILLS_ROOT / entry["source"]).is_file()


def test_companion_entries_are_not_soulmap_approval_entries() -> None:
    for entry in _manifest()["entries"]:
        if entry["source"].startswith("companion/"):
            assert "soulmap-compatible" not in entry["consumers"]


def test_companion_skill_files_have_required_front_matter_and_boundaries() -> None:
    forbidden = (
        "skills/meta/",
        "skills/frameworks/",
        "skills/safety/",
        "skills/voice/",
        "skills/brand/",
        "skills/spiritual/",
        "src/soulmap/",
    )
    for path in sorted(COMPANION_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert 'license: "MIT"' in text
        assert "# " in text
        assert not any(marker in text for marker in forbidden)
        behavior_text = "\n".join(
            line for line in text.splitlines() if not line.startswith("Avoid:")
        )
        assert "I will miss you" not in behavior_text
        assert "I need you" not in behavior_text


def test_companion_skill_family_has_identity_and_non_dependency_contracts() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in COMPANION_ROOT.glob("*.md")
    )
    for marker in (
        "AI companion",
        "human relationships",
        "exclusivity",
        "host's safety protocol",
        "person's agency",
    ):
        assert marker in text
