"""Contract between the SOULMAP.md priority table and the routing code.

`SOULMAP.md` ranks the primary frameworks, and `framework_selector.py` decides
between them. Until now that correspondence was maintained by eye: the existing
priority tests assert pairwise behavior ("grief outranks direction") but nothing
compared the doctrine table to the set of frameworks the selector can actually
emit.

This is the direction the Markdown and Python layers are allowed to interact.
Python reads doctrine and fails loudly when the two disagree. Python never
rewrites doctrine: `known-limitations.md` records that safety-relevant content
must be authored by humans and reviewable in Markdown, and that property only
holds while the Markdown is written by people.

Kept deliberately cheap to maintain. A framework's constant is derived from its
doctrine name, so adding one normally needs no change here at all. Only names
that cannot be derived are listed, and the derivation fails loudly rather than
guessing, so a rename surfaces as a test failure instead of a silent mismatch.
"""

from __future__ import annotations

import re

from soulmap.devtools.checks.check_api_docs import _source_primary_framework_values
from soulmap.devtools.support.repo import REPO_ROOT

_PRIORITY_ROW = re.compile(
    r"^\|\s*(Highest|Very high|High|Medium|Lower|Default)\s*\|\s*([^|]+?)\s*\|"
)

# Doctrine names a framework in prose; the selector names it as a constant.
# Most pairs follow one rule, so only the three that cannot be derived are
# listed. Keeping this list short is the point: a longer table would have to be
# edited every time a framework is added, and a check nobody wants to maintain
# stops being run.
#
# "De-escalation / Sanctuary" and "De-escalation" are two rows on purpose. They
# rank the same framework at two intensity levels, and the selector reaches both
# through one constant.
UNDERIVABLE_NAMES: dict[str, str] = {
    "de-escalation / sanctuary": "DE_ESCALATION",
    "dark night of the soul": "DARK_NIGHT_OF_SOUL",
    "integration and celebration": "INTEGRATION_CELEBRATION",
}


def _constant_for(doctrine_name: str) -> str:
    """Derive the routing constant a doctrine row refers to.

    Derivation is exact rather than fuzzy: the name is normalized to
    upper snake case and either matches an emitted constant or does not. A
    near-miss matcher could pair the wrong row with the wrong framework on a
    safety-ordered table and nothing downstream would notice.

    Args:
        doctrine_name: The framework name as written in the priority table,
            lowercased.

    Returns:
        The expected ``primary_framework`` constant.
    """
    if doctrine_name in UNDERIVABLE_NAMES:
        return UNDERIVABLE_NAMES[doctrine_name]
    return re.sub(r"[^a-z0-9]+", "_", doctrine_name).strip("_").upper()


def _doctrine_rows() -> list[tuple[str, str]]:
    """Read (tier, framework name) pairs from the SOULMAP.md priority table."""
    text = (REPO_ROOT / "SOULMAP.md").read_text(encoding="utf-8")
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = _PRIORITY_ROW.match(line)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip().lower()))
    return rows


def _ranked_constants() -> set[str]:
    return {_constant_for(name) for _, name in _doctrine_rows()}


def test_every_routed_framework_is_ranked_in_doctrine() -> None:
    """A framework the router can select must be ranked in doctrine.

    Failing here means the runtime can route somewhere the priority hierarchy
    does not rank, so nothing states what outranks it.
    """
    unranked = sorted(_source_primary_framework_values(REPO_ROOT) - _ranked_constants())
    assert not unranked, (
        "framework_selector.py can emit primary_framework value(s) with no row "
        f"in the SOULMAP.md priority table: {unranked}. Add the row, or map the "
        "name in UNDERIVABLE_NAMES if the constant cannot be derived from it."
    )


def test_every_ranked_framework_is_reachable_from_the_router() -> None:
    """A ranked framework must be one the router can actually emit.

    Failing here means doctrine ranks something unreachable, which reads to a
    reader as a capability the product does not have.
    """
    unreachable = sorted(
        _ranked_constants() - _source_primary_framework_values(REPO_ROOT)
    )
    assert not unreachable, (
        "SOULMAP.md ranks framework(s) the selector cannot emit: "
        f"{unreachable}. Either the row is stale, or the name needs an entry in "
        "UNDERIVABLE_NAMES."
    )


def test_doctrine_tiers_run_from_highest_to_default() -> None:
    """The table stays ordered, so reading it top-down gives real precedence.

    A row inserted in the wrong place would leave the table looking
    authoritative while describing an order the router does not follow.
    """
    order = ["Highest", "Very high", "High", "Medium", "Lower", "Default"]
    seen = [tier for tier, _ in _doctrine_rows()]
    positions = [order.index(tier) for tier in seen]

    assert positions == sorted(positions), (
        f"SOULMAP.md priority rows are not in descending tier order: {seen}"
    )


def test_secondary_layers_stay_out_of_the_primary_table() -> None:
    """Anger and somatic are secondary layers, so they are correctly unranked.

    This exists to stop a future reader "fixing" their absence. Both have real
    detectors, but the selector uses them only to set `secondary_layer` on a
    `DE_ESCALATION` selection. Adding them to the primary table would claim a
    routing behavior that does not exist.
    """
    emitted = _source_primary_framework_values(REPO_ROOT)

    assert "ANGER" not in emitted
    assert "SOMATIC" not in emitted
