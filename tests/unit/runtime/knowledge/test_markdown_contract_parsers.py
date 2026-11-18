from __future__ import annotations

from collections.abc import Callable

import pytest

from soulmap.runtime.knowledge import (
    celebration_source,
    orchestration_source,
    pattern_source,
    scope_source,
    synthesis_source,
)


@pytest.mark.parametrize(
    ("parser", "heading"),
    [
        (orchestration_source._contract_body, "Routing policy"),
        (scope_source._contract_body, "Scope policy"),
        (synthesis_source._contract_body, "Detection policy"),
        (celebration_source._contract_body, "Detection policy"),
    ],
)
def test_contract_boundaries_ignore_fenced_headings(
    parser: Callable[[str], str], heading: str
) -> None:
    source = (
        "```markdown\n"
        f"## {heading}\n"
        "## Fake boundary\n"
        "```\n"
        f"## {heading}\n"
        "Before the example.\n"
        "```markdown\n"
        "## Fake boundary\n"
        "```\n"
        "After the example.\n"
        "## Actual next section\n"
    )

    body = parser(source)

    assert "Before the example." in body
    assert "After the example." in body
    assert "Actual next section" not in body
    assert "Fake boundary" not in body


def test_orchestration_table_parser_ignores_fenced_table_rows() -> None:
    body = (
        "### Primary framework priority\n"
        "```markdown\n"
        "| Priority | Framework |\n"
        "| --- | --- |\n"
        "| 0 | FAKE |\n"
        "```\n"
        "| Priority | Framework |\n"
        "| --- | --- |\n"
        "| 1 | GRIEF |\n"
    )

    assert orchestration_source._table_rows(body, "Primary framework priority") == [
        ["1", "GRIEF"]
    ]


def test_scope_parser_ignores_fenced_groups_and_phrases() -> None:
    body = (
        "```markdown\n"
        "### Whitelist tier 1\n"
        "#### Fake category\n"
        '- "fake phrase"\n'
        "```\n"
        "### Whitelist tier 1\n"
        "#### Self-awareness\n"
        '- "real phrase"\n'
        "### Whitelist tier 2\n"
        "#### Work and purpose\n"
        '- "work phrase"\n'
        "### Blacklist layer 1\n"
        "#### Technical\n"
        '- "technical phrase"\n'
        "### Prohibited blacklist\n"
        "#### Jailbreak\n"
        '- "jailbreak phrase"\n'
    )

    values = scope_source._literal_config(body)

    assert values["WHITELIST_TIER1"] == {"self_awareness": ["real phrase"]}
    assert "fake phrase" not in str(values)


def test_synthesis_parsers_ignore_fenced_bullets_and_theme_groups() -> None:
    section = (
        "### Explicit request signals\n"
        "```markdown\n"
        '- "fake request"\n'
        "```\n"
        '- "real request"\n'
    )
    themes = (
        "### Recurring emotional theme signals\n"
        "```markdown\n"
        "#### Fake theme\n"
        '- "fake signal"\n'
        "```\n"
        "#### Loneliness\n"
        '- "real signal"\n'
    )

    assert synthesis_source._quoted_bullets(section, "Explicit request signals") == (
        "real request",
    )
    assert synthesis_source._theme_groups(themes, "Recurring emotional theme") == {
        "loneliness": ("real signal",)
    }


def test_celebration_parser_ignores_fenced_signal_bullets() -> None:
    body = (
        "### Negative overrides\n"
        "```markdown\n"
        '- "fake negative"\n'
        "```\n"
        '- "real negative"\n'
        "### Confirmation signals\n"
        '- "real confirmation"\n'
        "### Confirmation assistant anchors\n"
        '- "real anchor"\n'
    )

    assert celebration_source._knowledge_lists(body) == {
        "NEGATIVE_OVERRIDES": ("real negative",),
        "CONFIRMATION_SIGNALS": ("real confirmation",),
        "CONFIRMATION_ASSISTANT_ANCHORS": ("real anchor",),
    }


def test_pattern_parser_ignores_fenced_pattern_headings_and_signals() -> None:
    source = (
        "```markdown\n"
        "## Pattern 1: Fake pattern\n"
        "```\n"
        "## Pattern 1: Real pattern\n"
        "**What it looks like:** A real pattern.\n"
        "**Detection signals:**\n"
        '- "real signal"\n'
        "```markdown\n"
        "## Pattern 2: Fake nested pattern\n"
        '- "fake nested signal"\n'
        "```\n"
        "**Cycle phrases:**\n"
        '- "real cycle"\n'
    )

    patterns = pattern_source.parse_pattern_mapper(source)

    assert set(patterns) == {"real_pattern"}
    assert patterns["real_pattern"].keywords == ("real signal",)
    assert patterns["real_pattern"].cycle_phrases == ("real cycle",)
