"""Verify that generated output carries no non-public material.

This is defense in depth, and it is the layer that makes the promise in
`docs/web/CONTENT-MODEL.md` real. The allowlist decides what is loaded and the
loader strips internal sections, but both are code that can be wrong. This
module checks the bytes that would actually be published.

The detector phrases are read from `soulmap.runtime.config.safety` at check
time rather than copied here, so the guard keeps working when the phrase lists
change and never becomes a second copy of them.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from soulmap.runtime.config.safety import (
    DECISION_SEEKING,
    DEPENDENCY_KEYWORDS,
    ISOLATION_SIGNALS,
)

# Repository paths that must never be advertised on a public page. Naming an
# internal file tells a reader it exists and where to look, and a link to it
# resolves to nothing for anyone outside the repository.
FORBIDDEN_PATH_MARKERS: tuple[str, ...] = (
    "skills/meta/",
    "skills/safety/",
    "skills/spiritual/",
    "skills/soulmate/",
    "templates/",
    ".claude/",
    "src/soulmap/",
)

FORBIDDEN_HEADINGS: tuple[str, ...] = (
    "detection signals",
    "activation signals",
    "paired template",
)

# Phrases short enough to occur in ordinary prose. Matching them would produce
# constant false positives ("should i" appears in any reflective sentence), so
# the guard checks only phrases long enough to be distinctive.
_MINIMUM_PHRASE_WORDS = 4

# What makes a detector phrase dangerous in public is appearing in a *list* of
# phrases, which is what turns it into a usable evasion guide. A single
# illustrative quote inside explanatory prose is not that: `SOULMAP.md` Rule 3
# quotes one on purpose, and that file ships publicly in every extracted
# package. So the guard flags phrases that render as list items, plus any page
# carrying several distinct phrases at once, and ignores isolated prose
# mentions.
_LIST_ITEM_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.DOTALL | re.IGNORECASE)
_DENSITY_THRESHOLD = 3


@dataclass(frozen=True, slots=True)
class Leak:
    """One piece of non-public material found in generated output.

    Attributes:
        path: The generated file it was found in.
        kind: What category of leak it is.
        detail: The offending text.
    """

    path: Path
    kind: str
    detail: str


def _distinctive_detector_phrases(repo_root: Path | None = None) -> tuple[str, ...]:
    """Collect detector phrases specific enough to test for.

    Phrases that `SOULMAP.md` itself quotes are excluded. That file ships
    publicly in every extracted knowledge package, so a phrase it prints as an
    example is already public by the product's own decision, and flagging it on
    the website would be inconsistent with what the product already
    distributes. Rule 3 quotes a dependency signal for exactly this reason.

    Args:
        repo_root: Repository root, used to read the published doctrine. When
            omitted, no doctrine exemption is applied.

    Returns:
        Phrases of at least ``_MINIMUM_PHRASE_WORDS`` words, read live from the
        safety configuration, minus any the public doctrine already quotes.
    """
    phrases = (
        tuple(DEPENDENCY_KEYWORDS) + tuple(DECISION_SEEKING) + tuple(ISOLATION_SIGNALS)
    )
    distinctive = tuple(
        phrase for phrase in phrases if len(phrase.split()) >= _MINIMUM_PHRASE_WORDS
    )

    if repo_root is None:
        return distinctive

    # Collapse whitespace before comparing. Doctrine wraps its prose, so a
    # quoted example can straddle a line break: Rule 3's dependency example is
    # split after "who". Comparing raw text would miss it and report the
    # rendered page, where the same quote is one line, as a leak.
    doctrine = re.sub(
        r"\s+", " ", (repo_root / "SOULMAP.md").read_text(encoding="utf-8").lower()
    )
    return tuple(phrase for phrase in distinctive if phrase.lower() not in doctrine)


def check_output(site_root: Path, *, repo_root: Path | None = None) -> list[Leak]:
    """Scan generated HTML for material that must not be public.

    Args:
        site_root: The directory the site was written into.
        repo_root: Repository root, used to exempt phrases the public doctrine
            already quotes.

    Returns:
        Every leak found, in file order. An empty list means the output is
        clean.

    Raises:
        OSError: If a generated file cannot be read.
    """
    leaks: list[Leak] = []
    phrases = _distinctive_detector_phrases(repo_root)

    for path in sorted(site_root.rglob("*.html")):
        raw = path.read_text(encoding="utf-8")
        # Compare against unescaped text so an HTML-escaped quote or slash
        # cannot hide a phrase from the check.
        text = html.unescape(raw).lower()
        visible = re.sub(r"<[^>]+>", " ", text)

        list_text = " ".join(
            re.sub(r"<[^>]+>", " ", match).lower()
            for match in _LIST_ITEM_RE.findall(text)
        )
        listed = [phrase for phrase in phrases if phrase.lower() in list_text]
        for phrase in listed:
            leaks.append(Leak(path, "detector-phrase-list", phrase))

        present = {phrase for phrase in phrases if phrase.lower() in visible}
        if len(present) >= _DENSITY_THRESHOLD and not listed:
            leaks.append(
                Leak(
                    path,
                    "detector-phrase-density",
                    f"{len(present)} distinct phrases on one page",
                )
            )

        for heading in FORBIDDEN_HEADINGS:
            if re.search(rf"<h[1-6][^>]*>\s*{re.escape(heading)}", text):
                leaks.append(Leak(path, "internal-heading", heading))

        for marker in FORBIDDEN_PATH_MARKERS:
            if marker.lower() in text:
                leaks.append(Leak(path, "internal-path", marker))

    return leaks
