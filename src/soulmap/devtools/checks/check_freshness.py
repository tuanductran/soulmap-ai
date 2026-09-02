"""Markdown freshness checker for content that ages.

Some shipped content is tied to a moment. A strategy file written for one year
stops being current when that year ends, and a decision rule that hardcodes a
year silently drifts out of date while still reading as authoritative. Both
keep passing every other check in this repository, because nothing else knows
what "current" means.

This checker enforces what a file *declares* about its own shelf life, and
reports what it cannot judge:

``time_scope: "2026"``
    The file is written for that period. It fails once the period has passed.

``reviewed: "2026-08-31"``
    The file was last checked for accuracy on that date. It fails once it is
    older than the review window.

Declared dates fail. Undeclared years are reported and never fail, because a
year in prose is usually a citation ("a 2026 study from Drexel"), and a
citation naming its year stays correct forever. Failing on those would punish
correct content, so the split is deliberate: this layer states what it knows
and leaves the judgment to a person.

**No network.** Verifying whether a claim is still true needs a search, and
Python here does routing, detection, and enforcement only. The safety
enforcement matrix records the web-search source policy as ``guidance-only``
for exactly this reason. This checker finds what to look at; a maintainer, or
a surface that can search, decides what it means.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from soulmap.devtools.support.markdown import resolve_markdown_inputs

DEFAULT_REVIEW_WINDOW_DAYS = 365

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
_TIME_SCOPE_RE = re.compile(r'^time_scope:\s*"?(\d{4})"?\s*$', re.MULTILINE)
_REVIEWED_RE = re.compile(r'^reviewed:\s*"?(\d{4})-(\d{2})-(\d{2})"?\s*$', re.MULTILINE)

# A four-digit year that reads as a live threshold rather than a citation.
# "After 2024?" inside a decision rule is a rule that quietly went stale; "a
# 2024 study" is a citation that never does. Only the first shape is reported,
# and even then only as a report.
_OPERATIVE_YEAR_RE = re.compile(
    r"\b(?:after|before|since|as of|through|until)\s+(\d{4})\b", re.IGNORECASE
)


@dataclass(frozen=True)
class Finding:
    """One freshness problem or observation.

    Attributes:
        path: Repository-relative path of the file.
        message: Human-readable description.
        blocking: True when the finding fails the command.
    """

    path: str
    message: str
    blocking: bool


def _frontmatter(text: str) -> str:
    """Return the YAML front matter block, or an empty string when absent."""
    match = _FRONTMATTER_RE.match(text)
    return match.group(1) if match else ""


def check_text(
    text: str, relative_path: str, today: date, window_days: int
) -> list[Finding]:
    """Check one Markdown document's declared freshness.

    Args:
        text: Full file contents.
        relative_path: Repository-relative path, used in messages.
        today: The date to judge against, injected so tests are deterministic.
        window_days: How long a ``reviewed`` date stays valid.

    Returns:
        Every finding for this file, blocking and non-blocking.
    """
    findings: list[Finding] = []
    header = _frontmatter(text)

    scope = _TIME_SCOPE_RE.search(header)
    if scope:
        scope_year = int(scope.group(1))
        if today.year > scope_year:
            findings.append(
                Finding(
                    relative_path,
                    f"time_scope is {scope_year} but the year is now {today.year}. "
                    f"Rewrite the content for the current period or update the scope.",
                    blocking=True,
                )
            )

    reviewed = _REVIEWED_RE.search(header)
    if reviewed:
        year, month, day = (int(part) for part in reviewed.groups())
        age = (today - date(year, month, day)).days
        if age > window_days:
            findings.append(
                Finding(
                    relative_path,
                    f"last reviewed {age} days ago, over the {window_days}-day "
                    f"window. Re-check the claims, then update the reviewed date.",
                    blocking=True,
                )
            )

    for match in _OPERATIVE_YEAR_RE.finditer(text):
        if int(match.group(1)) < today.year:
            findings.append(
                Finding(
                    relative_path,
                    f"reads {match.group(0)!r}, a threshold older than the current "
                    f"year. Check whether this rule still means what it says.",
                    blocking=False,
                )
            )

    return findings


def check_paths(
    paths: list[Path], root: Path, today: date, window_days: int
) -> list[Finding]:
    """Check every given Markdown file.

    Args:
        paths: Markdown files to check.
        root: Repository root, used to build relative paths for messages.
        today: The date to judge against.
        window_days: How long a ``reviewed`` date stays valid.

    Returns:
        Findings across all files, in path order.
    """
    findings: list[Finding] = []
    for path in sorted(paths):
        relative = (
            path.relative_to(root).as_posix()
            if path.is_relative_to(root)
            else str(path)
        )
        findings.extend(
            check_text(path.read_text(encoding="utf-8"), relative, today, window_days)
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    """Run the freshness check from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when nothing blocking is found, 1 otherwise. Non-blocking findings
        are printed but never change the exit code.
    """
    parser = argparse.ArgumentParser(prog="soulmap check-freshness")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(),
        help="Repo root (default: current directory).",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=DEFAULT_REVIEW_WINDOW_DAYS,
        help=f"Review window in days (default: {DEFAULT_REVIEW_WINDOW_DAYS}).",
    )
    parser.add_argument(
        "paths", nargs="*", help="Optional Markdown files or directories."
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    findings = check_paths(
        resolve_markdown_inputs(root, args.paths),
        root,
        datetime.now(tz=UTC).date(),
        args.window_days,
    )

    blocking = [finding for finding in findings if finding.blocking]
    advisory = [finding for finding in findings if not finding.blocking]

    for finding in advisory:
        print(f"note: {finding.path}: {finding.message}")
    for finding in blocking:
        print(f"{finding.path}: {finding.message}")

    if blocking:
        print(f"\n{len(blocking)} file(s) need a freshness review.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
