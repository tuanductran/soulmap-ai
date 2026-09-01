"""The trusted-source list must keep evidence and perspective separated.

`skills/safety/whitelist-blacklist-system.md` tells the deployed AI surface
which domains it may cite when web search is enabled. Python performs no web
search, so nothing at runtime can check a citation; the safety matrix records
that row as `guidance-only`. This contract is the only automated protection the
split has, so it pins the structure rather than the prose.

The specific regression it exists to catch: the list once carried a single
category named "Science and energy research" holding `heartmath.org` and
`noetic.org` alongside `nature.com` and `nih.gov`. A heading named "Science"
lends an organization's own research the weight of peer review, which is what
Category 3 of `skills/meta/epistemic-guardrails.md` and the
`spiritual_claim_as_fact` response guard exist to prevent.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCTRINE = REPO_ROOT / "skills" / "safety" / "whitelist-blacklist-system.md"

_TIER_1_HEADING = "**Trusted sources, tier 1, citable as evidence:**"
_TIER_2_HEADING = "**Trusted sources, tier 2, citable as perspective only:**"
_CLAIM_LIMIT_HEADING = "**A listed domain does not make a claim citable.**"

# Rows are split on the pipe rather than matched with a regex. The Markdown
# formatter pads table cells to align columns, so the gaps around the
# separators vary from row to row, and the obvious regex for that
# (`\s*` around a lazy `.+?`) is a polynomial-backtracking pattern: `.` matches
# whitespace too, so the two quantifiers overlap and CodeQL flags it. Splitting
# is linear, and it is simpler than the regex it replaces.

# Organizations that report their own research. Doctrine may cite them, but
# never from a category that implies peer review.
_PERSPECTIVE_ONLY_DOMAINS = frozenset({"heartmath.org", "noetic.org"})


def _doctrine_text() -> str:
    """Read the shipped source-policy file."""
    return DOCTRINE.read_text(encoding="utf-8")


def _tier_table(text: str, heading: str, *, until: str) -> dict[str, set[str]]:
    """Parse one tier's table into a category-to-domains mapping.

    Scoping matters here. `heartmath.org` is also named in the citation rules
    above these tables, as the worked example of how to cite an advocacy
    organization. A substring search over the whole file would find it and
    prove nothing, so the parse is bounded to the table that follows the
    heading.

    Args:
        text: Full doctrine file text.
        heading: The bold tier heading that opens the table.
        until: The marker that closes the section.

    Returns:
        A mapping of category name to the set of domains listed for it.
    """
    start = text.index(heading) + len(heading)
    section = text[start : text.index(until, start)]

    table: dict[str, set[str]] = {}
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 2:
            continue
        category, domains = cells
        if not (category.startswith("**") and category.endswith("**")):
            continue
        table[category.strip("*").strip()] = {
            domain.strip() for domain in domains.split(",") if domain.strip()
        }
    return table


def _tier_1(text: str) -> dict[str, set[str]]:
    """Return the tier 1 table, the sources citable as evidence."""
    return _tier_table(text, _TIER_1_HEADING, until=_TIER_2_HEADING)


def _tier_2(text: str) -> dict[str, set[str]]:
    """Return the tier 2 table, the sources citable as perspective only."""
    return _tier_table(text, _TIER_2_HEADING, until=_CLAIM_LIMIT_HEADING)


def test_both_tiers_parse_into_real_tables() -> None:
    """A parser matching nothing would make every assertion below vacuous."""
    text = _doctrine_text()
    tier_1, tier_2 = _tier_1(text), _tier_2(text)

    assert len(tier_1) >= 3, f"tier 1 parsed only {len(tier_1)} categories"
    assert len(tier_2) >= 4, f"tier 2 parsed only {len(tier_2)} categories"
    for category, domains in {**tier_1, **tier_2}.items():
        assert domains, f"category {category!r} parsed with no domains"


def test_self_reporting_organizations_stay_out_of_the_evidence_tier() -> None:
    """The regression this file exists for.

    `noetic.org` is a parapsychological research institute and `heartmath.org`
    reports its own research. Either one sitting in tier 1 would let SoulMap
    cite it as evidence, which is the framing Category 3 of the epistemic
    guardrails prohibits.
    """
    text = _doctrine_text()
    evidence_domains = set().union(*_tier_1(text).values())

    leaked = _PERSPECTIVE_ONLY_DOMAINS & evidence_domains
    assert not leaked, (
        f"self-reporting organizations found in the evidence tier: {sorted(leaked)}. "
        f"These belong in tier 2, cited as perspective and named as organizations."
    )


def test_self_reporting_organizations_are_still_listed_as_perspective() -> None:
    """They are not banned, only tiered. Dropping them is a different change."""
    text = _doctrine_text()
    perspective_domains = set().union(*_tier_2(text).values())

    missing = _PERSPECTIVE_ONLY_DOMAINS - perspective_domains
    assert not missing, f"expected these in tier 2, not found: {sorted(missing)}"


def test_no_tier_1_category_name_implies_science_it_does_not_have() -> None:
    """A category heading is what lends a source its epistemic weight.

    The original defect was the heading, not the domains. "Science and energy
    research" made a parapsychology institute read as a peer-reviewed source.
    Any tier 1 category claiming science must hold only peer-reviewed
    publishers and clinical bodies.
    """
    text = _doctrine_text()
    for category, domains in _tier_1(text).items():
        if "scien" not in category.lower():
            continue
        overlap = _PERSPECTIVE_ONLY_DOMAINS & domains
        assert not overlap, (
            f"category {category!r} names science but lists {sorted(overlap)}"
        )


def test_claim_level_limits_override_the_domain_list() -> None:
    """The policy was domain-based, so a harmful claim on a listed domain passed.

    Publishers in tier 2 carry the position that illness is caused by thought
    or emotion and heals without medical care, which the Layer 4 anti-medicine
    row calls life-threatening. The domains stay listed, so these three limits
    are what actually holds the line.
    """
    text = _doctrine_text()
    limits = text[text.index(_CLAIM_LIMIT_HEADING) :]

    for phrase in (
        "illness is caused by thought",
        "heals without medical care",
        "anti-medicine category",
        "identity, destiny",
        "past life happened",
    ):
        assert phrase in limits, f"claim-level limits no longer state: {phrase!r}"


def test_crisis_search_points_at_a_source_with_country_pages() -> None:
    """Crisis search is the one case doctrine marks MUST search immediately."""
    text = _doctrine_text()
    crisis = text[text.index("**Crisis search:**") :]

    crisis_hosts = {
        parsed.hostname.lower()
        for parsed in (
            urlparse(match.group(0)) for match in re.finditer(r"https?://[^\s)>\]]+", crisis)
        )
        if parsed.hostname
    }
    assert any(
        host == "findahelpline.com" or host.endswith(".findahelpline.com")
        for host in crisis_hosts
    )
    assert "Vietnam" in crisis, "the first crisis line SoulMap lists is unnamed"

    tier_1_hosts = set()
    for value in set().union(*_tier_1(text).values()):
        candidate = value if "://" in value else f"https://{value}"
        parsed = urlparse(candidate)
        if parsed.hostname:
            tier_1_hosts.add(parsed.hostname.lower())

    assert "findahelpline.com" in tier_1_hosts
