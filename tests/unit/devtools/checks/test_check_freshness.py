from __future__ import annotations

from datetime import date

import pytest

from soulmap.devtools.checks.check_freshness import (
    DEFAULT_REVIEW_WINDOW_DAYS,
    check_text,
)

_TODAY = date(2026, 8, 31)


def _messages(text: str, *, today: date = _TODAY, window: int = 365) -> list[str]:
    return [f.message for f in check_text(text, "x.md", today, window)]


def _blocking(text: str, *, today: date = _TODAY, window: int = 365) -> list[str]:
    return [f.message for f in check_text(text, "x.md", today, window) if f.blocking]


def test_a_time_scope_in_the_past_blocks() -> None:
    text = '---\nname: "s"\ntime_scope: "2025"\n---\n\n# Strategy\n'

    assert len(_blocking(text)) == 1
    assert "2025" in _blocking(text)[0]


def test_the_current_years_time_scope_passes() -> None:
    """A file written for this year is current until the year ends."""
    text = '---\nname: "s"\ntime_scope: "2026"\n---\n\n# Strategy\n'

    assert _blocking(text) == []


def test_a_time_scope_rolls_over_on_the_first_day_of_the_next_year() -> None:
    """The boundary is what makes this check worth having.

    A 2026 strategy file is correct on 2026-12-31 and stale on 2027-01-01, and
    nothing else in the repository notices the difference.
    """
    text = '---\nname: "s"\ntime_scope: "2026"\n---\n\n# Strategy\n'

    assert _blocking(text, today=date(2026, 12, 31)) == []
    assert len(_blocking(text, today=date(2027, 1, 1))) == 1


def test_a_reviewed_date_past_the_window_blocks() -> None:
    text = '---\nname: "s"\nreviewed: "2025-01-01"\n---\n\n# Doc\n'

    blocking = _blocking(text)
    assert len(blocking) == 1
    assert "window" in blocking[0]


def test_a_recent_reviewed_date_passes() -> None:
    text = '---\nname: "s"\nreviewed: "2026-08-01"\n---\n\n# Doc\n'

    assert _blocking(text) == []


def test_the_review_window_is_configurable() -> None:
    """The same file passes or fails depending only on the window."""
    text = '---\nname: "s"\nreviewed: "2026-01-01"\n---\n\n# Doc\n'

    assert _blocking(text, window=365) == []
    assert len(_blocking(text, window=30)) == 1


def test_a_file_declaring_nothing_is_never_blocked() -> None:
    """Silence is not a failure.

    Most shipped content does not age on a schedule. Requiring a declaration
    everywhere would add noise to 70-odd files to catch the handful that do.
    """
    text = '---\nname: "s"\n---\n\n# Doc\n\nA 2024 study found something.\n'

    assert _blocking(text) == []


@pytest.mark.parametrize(
    "prose",
    [
        "A 2026 study from Drexel analyzed 318 Reddit posts.",
        "Published in Science, March 2026.",
        "Multiple peer-reviewed studies (2024-2026) documented this.",
        "OpenAI System Prompt Best Practices (2024)",
        "In November 2025, a deletion screen drew criticism.",
    ],
    ids=["study-year", "journal-date", "year-range", "parenthetical", "month-year"],
)
def test_citation_years_are_never_reported(prose: str) -> None:
    """A citation naming its year stays correct forever.

    These are the real sentences from `skills/brand/research-backing.md`. A
    year-matching rule that flagged them would punish correct, well-sourced
    content, which is why only operative thresholds are reported.
    """
    text = f'---\nname: "s"\n---\n\n# Doc\n\n{prose}\n'

    assert _messages(text) == []


@pytest.mark.parametrize(
    "rule",
    [
        "Check: (a) After 2024? (b) Crisis resources needed?",
        "Event or study after 2024 needs verification.",
        "Anything since 2023 should be searched.",
        "Valid until 2025 for this purpose.",
    ],
    ids=["decision-step", "policy-row", "since", "until"],
)
def test_operative_year_thresholds_are_reported(rule: str) -> None:
    """A rule with a frozen year keeps reading as authoritative while drifting.

    This is the defect that prompted the checker: the scope doctrine asked
    "After 2024?" as a live search trigger two years after 2024.
    """
    text = f'---\nname: "s"\n---\n\n# Doc\n\n{rule}\n'

    assert len(_messages(text)) == 1


def test_an_operative_threshold_reports_but_does_not_block() -> None:
    """Reported, not enforced, because the checker cannot judge intent.

    Deciding whether a threshold still means what it says needs a person, or a
    surface that can search. Python here detects; it never fetches.
    """
    text = '---\nname: "s"\n---\n\n# Doc\n\nEvent or study after 2024.\n'

    findings = check_text(text, "x.md", _TODAY, 365)
    assert len(findings) == 1
    assert findings[0].blocking is False


def test_a_future_or_current_threshold_is_not_reported() -> None:
    text = '---\nname: "s"\n---\n\n# Doc\n\nAnything after 2026 needs review.\n'

    assert _messages(text) == []


def test_the_default_window_is_a_year() -> None:
    assert DEFAULT_REVIEW_WINDOW_DAYS == 365
