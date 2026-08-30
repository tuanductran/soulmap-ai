"""Contract between the SOULMAP.md priority table and the routing code.

`SOULMAP.md` ranks the primary frameworks, and `framework_selector.py` decides
between them. Until now that correspondence was maintained by eye: the existing
priority tests assert pairwise behavior ("grief outranks direction") but nothing
compared the doctrine table to the set of frameworks the selector can actually
emit.

This is the direction the Markdown and Python layers are allowed to interact.
Python reads doctrine and fails loudly when the two disagree. Python never
rewrites doctrine: `known-limitations.md` records that safety-relevant content
"must be authored by humans" and reviewable in Markdown, and that property only
holds while the Markdown is written by people.
"""

from __future__ import annotations

import re

from soulmap.devtools.checks.check_api_docs import _source_primary_framework_values
from soulmap.devtools.support.repo import REPO_ROOT

_PRIORITY_ROW = re.compile(
    r"^\|\s*(Highest|Very high|High|Medium|Lower|Default)\s*\|\s*([^|]+?)\s*\|"
)

# Doctrine names the frameworks in prose; the selector names them as constants.
# The mapping is explicit rather than derived, because a near-miss string match
# on a safety-ordered table could silently pair the wrong row with the wrong
# framework, and nothing downstream would notice.
#
# "De-escalation / Sanctuary" and "De-escalation" are two rows on purpose: they
# rank the same framework at two intensity levels, and the selector reaches both
# through one constant.
DOCTRINE_TO_CONSTANT: dict[str, str] = {
    "crisis": "CRISIS",
    "dependency": "DEPENDENCY",
    "de-escalation / sanctuary": "DE_ESCALATION",
    "de-escalation": "DE_ESCALATION",
    "grief": "GRIEF",
    "existential": "EXISTENTIAL",
    "inner parts": "INNER_PARTS",
    "direction": "DIRECTION",
    "creative drought": "CREATIVE_DROUGHT",
    "perfectionism paralysis": "PERFECTIONISM_PARALYSIS",
    "shadow": "SHADOW",
    "ancestral patterns": "ANCESTRAL_PATTERNS",
    "fear of visibility": "FEAR_OF_VISIBILITY",
    "empath boundary": "EMPATH_BOUNDARY",
    "dark night of the soul": "DARK_NIGHT_OF_SOUL",
    "soul nourishment": "SOUL_NOURISHMENT",
    "divine guidance": "DIVINE_GUIDANCE",
    "sacred polarity": "SACRED_POLARITY",
    "spiritual purpose": "SPIRITUAL_PURPOSE",
    "soulmate longing": "SOULMATE_LONGING",
    "partnership patterns": "PARTNERSHIP_PATTERNS",
    "meaning integration": "MEANING_INTEGRATION",
    "integration and celebration": "INTEGRATION_CELEBRATION",
    "synthesis": "SYNTHESIS",
    "pattern": "PATTERN",
    "mirror": "MIRROR",
}


def _doctrine_rows() -> list[tuple[str, str]]:
    """Read (tier, framework name) pairs from the SOULMAP.md priority table."""
    text = (REPO_ROOT / "SOULMAP.md").read_text(encoding="utf-8")
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = _PRIORITY_ROW.match(line)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip().lower()))
    return rows


def test_every_doctrine_row_maps_to_a_known_framework_constant() -> None:
    """A framework added to doctrine must be given a routing constant.

    Failing here means `SOULMAP.md` promises a framework the router cannot
    select, which is a promise the product cannot keep.
    """
    unmapped = [
        name for _, name in _doctrine_rows() if name not in DOCTRINE_TO_CONSTANT
    ]
    assert not unmapped, (
        "SOULMAP.md priority rows with no routing constant: "
        f"{unmapped}. Add the framework to framework_selector.py and map it here."
    )


def test_every_routed_framework_is_ranked_in_doctrine() -> None:
    """A framework the router can select must be ranked in doctrine.

    Failing here means the runtime can route somewhere the priority hierarchy
    does not rank, so nobody can tell what outranks it.
    """
    # Unmapped names are reported by the mapping test above. Skipping them here
    # keeps that one failure readable instead of crashing every other test with
    # a KeyError that names the symptom rather than the cause.
    ranked = {
        DOCTRINE_TO_CONSTANT[name]
        for _, name in _doctrine_rows()
        if name in DOCTRINE_TO_CONSTANT
    }
    emitted = _source_primary_framework_values(REPO_ROOT)

    unranked = sorted(emitted - ranked)
    assert not unranked, (
        "framework_selector.py can emit primary_framework value(s) with no row "
        f"in the SOULMAP.md priority table: {unranked}."
    )


def test_every_ranked_framework_is_reachable_from_the_router() -> None:
    """A ranked framework must be one the router can actually emit.

    Failing here means doctrine ranks something unreachable, which reads as a
    capability the product does not have.
    """
    # Unmapped names are reported by the mapping test above. Skipping them here
    # keeps that one failure readable instead of crashing every other test with
    # a KeyError that names the symptom rather than the cause.
    ranked = {
        DOCTRINE_TO_CONSTANT[name]
        for _, name in _doctrine_rows()
        if name in DOCTRINE_TO_CONSTANT
    }
    emitted = _source_primary_framework_values(REPO_ROOT)

    unreachable = sorted(ranked - emitted)
    assert not unreachable, (
        f"SOULMAP.md ranks framework(s) the selector cannot emit: {unreachable}."
    )


def test_doctrine_tiers_run_from_highest_to_default() -> None:
    """The table stays ordered, so reading it top-down gives real precedence.

    A row inserted in the wrong place would make the table look authoritative
    while describing an order the router does not follow.
    """
    order = ["Highest", "Very high", "High", "Medium", "Lower", "Default"]
    seen = [tier for tier, _ in _doctrine_rows()]
    positions = [order.index(tier) for tier in seen]

    assert positions == sorted(positions), (
        f"SOULMAP.md priority rows are not in descending tier order: {seen}"
    )


def test_secondary_layers_are_not_expected_in_the_primary_table() -> None:
    """Anger and somatic are secondary layers, so they are correctly unranked.

    This test exists to stop a future reader "fixing" their absence. Both have
    real detectors, but the selector uses them only to set `secondary_layer` on
    a `DE_ESCALATION` selection, never to set `primary_framework`. Adding them
    to the primary table would claim a routing behavior that does not exist.
    """
    emitted = _source_primary_framework_values(REPO_ROOT)

    assert "ANGER" not in emitted
    assert "SOMATIC" not in emitted

    selector = (
        REPO_ROOT / "src" / "soulmap" / "runtime" / "routing" / "framework_selector.py"
    ).read_text(encoding="utf-8")
    assert '"anger"' in selector, "anger is still expected as a secondary layer"
    assert '"somatic"' in selector, "somatic is still expected as a secondary layer"
