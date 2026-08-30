"""Extract public doctrine structures from SOULMAP.md.

The safety page and the architecture page are generated from doctrine rather
than written separately, so the site cannot drift from the rules the product
actually enforces. Restating them in a template would create a second source of
truth for safety wording, which is exactly what `repo-contract.md` forbids.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# **Rule 1, crisis response:** On any immediate crisis signal ...
_RULE_RE = re.compile(r"^\*\*Rule (\d+), ([^:*]+):\*\*\s*(.*)$")

_TIER_NOTES: dict[str, str] = {
    "Highest": "Crisis. Immediate crisis signals are present",
    "Very high": "Dependency risk, or high emotional intensity and serious destabilization",
    "High": "Acute grief, or moderate emotional intensity",
    "Medium": "The reflective frameworks, chosen by the signals present",
    "Lower": "Synthesis and pattern work, when the user has capacity",
    "Default": "Mirror. The standard reflective posture",
}


@dataclass(frozen=True, slots=True)
class SafetyRule:
    """One numbered non-negotiable rule from doctrine.

    Attributes:
        number: The rule's number as written in doctrine.
        title: The rule's short name, for example ``"crisis response"``.
        body: The rule text, with Markdown emphasis stripped.
    """

    number: int
    title: str
    body: str


@dataclass(frozen=True, slots=True)
class PriorityTier:
    """One tier of the routing priority hierarchy.

    Attributes:
        label: The tier name as written in doctrine, for example ``"Medium"``.
        slug: URL-safe form of the label.
        note: A short plain description of what the tier covers.
    """

    label: str
    slug: str
    note: str


def load_safety_rules(repo_root: Path) -> list[SafetyRule]:
    """Read the numbered non-negotiable safety rules from doctrine.

    Only the rule's first paragraph is taken. Later paragraphs under a rule
    carry operational detail, including the crisis-line list that the site's
    footer already shows, and reproducing them inline would make the page a
    second copy of doctrine rather than a readable summary of it.

    Args:
        repo_root: Repository root.

    Returns:
        The rules in doctrine order.

    Raises:
        OSError: If SOULMAP.md cannot be read.
    """
    lines = (repo_root / "SOULMAP.md").read_text(encoding="utf-8").splitlines()
    rules: list[SafetyRule] = []

    for index, line in enumerate(lines):
        match = _RULE_RE.match(line.strip())
        if not match:
            continue

        # A rule runs to the next blank line. Taking only the matched line
        # would cut every multi-line rule mid-sentence.
        body_parts = [match.group(3).strip()]
        for following in lines[index + 1 :]:
            if not following.strip():
                break
            body_parts.append(following.strip())

        rules.append(
            SafetyRule(
                number=int(match.group(1)),
                title=match.group(2).strip(),
                body=re.sub(r"\*\*|`", "", " ".join(body_parts).strip()),
            )
        )

    return rules


def priority_tiers(tiers_in_use: set[str]) -> list[PriorityTier]:
    """Build the ordered tier list for grouping and display.

    Args:
        tiers_in_use: Tier labels that at least one public page carries.

    Returns:
        Tiers in doctrine priority order, highest first, limited to those in
        use plus a trailing group for documents with no doctrine row.
    """
    order = ("Highest", "Very high", "High", "Medium", "Lower", "Default")
    return [
        PriorityTier(
            label=label,
            slug=label.lower().replace(" ", "-"),
            note=_TIER_NOTES.get(label, ""),
        )
        for label in order
        if label in tiers_in_use
    ]
