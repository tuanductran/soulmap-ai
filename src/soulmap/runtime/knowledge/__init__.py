"""Loaders that turn shipped Markdown skills into runtime data structures.

Python in this package never hardcodes SoulMap's clinical/reflective content.
It reads that content from the Markdown files under ``skills/`` so the two stay
in sync by construction — see AGENTS.md, "primary content is Markdown".
"""

from .soulmate_skills import (
    MAX_ARCHIVE_MEMBERS,
    MAX_ARCHIVE_TOTAL_SIZE,
    MAX_MANIFEST_BYTES,
    MAX_SKILL_BYTES,
    SOULMAP_COMPATIBLE_SKILL_IDS,
    LoadedSoulmateSkill,
    SoulMapSoulmateAdapter,
    SoulmateSkillLoader,
    SoulmateSkillLoadError,
)

__all__ = [
    "MAX_ARCHIVE_MEMBERS",
    "MAX_ARCHIVE_TOTAL_SIZE",
    "MAX_MANIFEST_BYTES",
    "MAX_SKILL_BYTES",
    "SOULMAP_COMPATIBLE_SKILL_IDS",
    "LoadedSoulmateSkill",
    "SoulMapSoulmateAdapter",
    "SoulmateSkillLoadError",
    "SoulmateSkillLoader",
]
