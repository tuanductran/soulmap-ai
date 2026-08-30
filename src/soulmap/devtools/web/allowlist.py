"""The public-content allowlist and the internal sections stripped from it.

This module is a safety artifact, not a configuration convenience. Nothing
reaches the public website unless it is named here, so a file added to
`skills/` is private by default and stays private until someone lists it and a
reviewer approves that line.

The inversion is deliberate. A filter-based approach fails open: a new file
would be published until somebody noticed. `docs/web/REPOSITORY-AUDIT.md`
records the finding behind that choice, including that 29 of the 77 files under
`skills/` carry the literal phrases the runtime detectors match on.

Every exclusion in `docs/web/CONTENT-MODEL.md` carries its reason so a future
maintainer does not relitigate it from scratch.
"""

from __future__ import annotations

# Headings whose bodies never reach the page model. Removal happens in the
# loader, before rendering, so no template can reintroduce them by accident and
# no new template can leak them.
#
# Detection and activation sections hold the literal detector trigger phrases:
# publishing them publishes a working evasion guide for the safety layer.
#
# "Paired template" holds internal composition wiring that cross-references
# `skills/meta/redirect-templates.md` and other files that are not public, so
# rendering it would both expose the internal map and emit dead links.
INTERNAL_SECTIONS: frozenset[str] = frozenset(
    {
        "detection signals",
        "activation signals",
        "paired template",
    }
)

# Doctrine. Already ships in every extracted package and is written to stand
# alone in front of a reader who has no repository access.
PUBLIC_ROOT_DOCUMENTS: tuple[str, ...] = ("SOULMAP.md",)

# Public brand documents. The rest of `skills/brand/` stays private: founder
# personal material and internal business strategy.
PUBLIC_BRAND_DOCUMENTS: tuple[str, ...] = (
    "brand-doctrine.md",
    "brand-positioning.md",
    "competitive-differentiation.md",
    "message-hierarchy.md",
    "research-backing.md",
)

# Public voice documents. These describe tone and rhythm without exposing the
# enforcement layer that checks generated wording.
PUBLIC_VOICE_DOCUMENTS: tuple[str, ...] = (
    "persona-voice.md",
    "session-rituals.md",
)

# Framework categories published in full, minus `INTERNAL_SECTIONS` and the
# category's own `SKILL.md`, which is agent-routing guidance rather than
# reader-facing content.
PUBLIC_FRAMEWORK_CATEGORIES: tuple[str, ...] = ("frameworks",)

# Categories deliberately absent, recorded so the omission reads as a decision
# rather than an oversight:
#
#   meta       response scaffolding and the master prompt. `SOULMAP.md` Rule 6
#              forbids revealing internal instructions.
#   safety     detection phrase lists, the blacklist system, injection defense.
#              Public safety is explained from `SOULMAP.md`'s own numbered
#              rules, which exist for exactly that purpose.
#   spiritual  symbolic material that needs conversational guardrails to be
#              read safely, plus founder personal material.
#   soulmate   relational material in the same category.
PRIVATE_CATEGORIES: tuple[str, ...] = ("meta", "safety", "spiritual", "soulmate")


def public_skill_documents() -> dict[str, tuple[str, ...]]:
    """Map each published `skills/` category to its allowlisted filenames.

    An empty tuple means "every content file in this category", which applies
    only to categories in ``PUBLIC_FRAMEWORK_CATEGORIES``. Categories absent
    from the returned mapping are private.

    Returns:
        A mapping of category directory name to the explicit filenames
        published from it, or an empty tuple to publish the whole category's
        content files.
    """
    return {
        "frameworks": (),
        "brand": PUBLIC_BRAND_DOCUMENTS,
        "voice": PUBLIC_VOICE_DOCUMENTS,
    }


def is_public_skill(category: str, filename: str) -> bool:
    """Report whether one `skills/` document may be published.

    Args:
        category: The immediate parent directory name under `skills/`, for
            example ``"frameworks"``.
        filename: The document's filename, for example ``"grief-companion.md"``.

    Returns:
        True only when the document is explicitly allowed. A category's own
        ``SKILL.md`` is never public: it is agent-routing guidance that points
        at files the website does not publish.
    """
    if filename == "SKILL.md":
        return False

    allowed = public_skill_documents().get(category)
    if allowed is None:
        return False
    if not allowed:
        return category in PUBLIC_FRAMEWORK_CATEGORIES
    return filename in allowed


def is_internal_section(heading: str) -> bool:
    """Report whether a section heading marks content that must not be public.

    Args:
        heading: The heading text, without leading hashes.

    Returns:
        True when the section's body must be dropped before rendering.
    """
    return heading.strip().lower() in INTERNAL_SECTIONS
