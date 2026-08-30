"""The safety enforcement matrix's status column must mean what it says.

`docs/engineering/safety-enforcement-matrix.md` grades every AGENTS.md rule
against real code, tests, and evals. Phase 14 of the roadmap split `partial`
into two meanings: a real gap achievable inside this package (still
`partial`), and a gap bounded by the package's own architecture, which no new
Python code closes (`bounded`). A row using a status token the legend does not
define, or a `bounded` row that does not name the boundary it is bounded by,
would misstate what the code can do.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX = REPO_ROOT / "docs" / "engineering" / "safety-enforcement-matrix.md"
KNOWN_LIMITATIONS = REPO_ROOT / "docs" / "engineering" / "known-limitations.md"

_BOUNDARY_HEADING = "AI response generation"
_BOUNDARY_CITATION = '`docs/engineering/known-limitations.md`, "AI response generation"'
_LEGEND_STATUS_RE = re.compile(r"^- `([a-z-]+)`:", re.MULTILINE)
_ROW_STATUS_RE = re.compile(r"^\| .+ \| `([a-z-]+)` \| .+ \|$")


def _matrix_text() -> str:
    """Read the matrix file once, resolved from the repository root."""
    return MATRIX.read_text(encoding="utf-8")


def _legend_statuses(text: str) -> set[str]:
    """Return every status token the "Status values" legend documents."""
    legend = text.split("Status values:", 1)[1].split("| `SOULMAP.md` rule", 1)[0]
    return set(_LEGEND_STATUS_RE.findall(legend))


def _table_rows(text: str) -> list[str]:
    """Return every data row of the matrix table, header and separator excluded."""
    table = text.split("| `SOULMAP.md` rule", 1)[1].split("\n## How to use", 1)[0]
    lines = table.splitlines()
    return [line for line in lines[2:] if line.startswith("|")]


def test_every_status_token_is_a_documented_legend_value() -> None:
    """A row cannot claim a status the legend never defines."""
    text = _matrix_text()
    legend = _legend_statuses(text)
    assert legend, "the legend parser found no status tokens, check the anchors"

    undocumented: list[str] = []
    for row in _table_rows(text):
        match = _ROW_STATUS_RE.match(row)
        assert match, f"row does not match the expected 6-column shape: {row!r}"
        status = match.group(1)
        if status not in legend:
            undocumented.append(status)

    assert not undocumented, (
        f"status tokens used in the table but missing from the legend: "
        f"{sorted(set(undocumented))}"
    )


def test_every_bounded_row_cites_the_document_recording_its_boundary() -> None:
    """A `bounded` row must name the doc section that records why it is bounded.

    Without the citation, `bounded` reads as an excuse rather than evidence: a
    reader has no way to check that the boundary is real architecture, not a
    gap someone gave up on.
    """
    text = _matrix_text()
    uncited: list[str] = []

    for row in _table_rows(text):
        match = _ROW_STATUS_RE.match(row)
        assert match
        if match.group(1) != "bounded":
            continue
        if _BOUNDARY_CITATION not in row:
            uncited.append(row.split("|")[1].strip())

    assert not uncited, f"bounded rows missing the boundary citation: {uncited}"


def test_the_cited_boundary_section_actually_exists() -> None:
    """The citation must resolve, so a renamed heading cannot go unnoticed."""
    content = KNOWN_LIMITATIONS.read_text(encoding="utf-8")
    assert f"## {_BOUNDARY_HEADING}" in content


def test_the_row_parser_is_not_silently_matching_nothing() -> None:
    """A parser that matches zero rows would make the tests above pass vacuously.

    ``guidance-only`` is deliberately not asserted to have a row: it is a legend
    entry reserved for a doctrine rule with no code enforcement at all, and every
    rule currently documented already has some. A future rule may use it; that is
    not a drift signal the way an unparsed table would be.
    """
    text = _matrix_text()
    rows = _table_rows(text)

    assert len(rows) >= 20, f"expected the full matrix, parsed only {len(rows)} rows"
    statuses = {_ROW_STATUS_RE.match(row).group(1) for row in rows}  # type: ignore[union-attr]
    assert statuses == {"enforced", "partial", "bounded"}
