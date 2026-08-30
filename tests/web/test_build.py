"""Structural tests for the website build."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.devtools.web.build import build_site
from soulmap.devtools.web.content import (
    build_page,
    load_priority_tiers,
    load_public_pages,
)
from soulmap.devtools.web.doctrine import load_safety_rules


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("site") / "site"
    build_site(output)
    return output


def test_build_writes_every_expected_route(site: Path) -> None:
    for route in (
        "index.html",
        "404.html",
        "frameworks/index.html",
        "safety/index.html",
        "architecture/index.html",
        "about/index.html",
        "style.css",
        "search.js",
        "sitemap.xml",
        "robots.txt",
        "search-index.json",
    ):
        assert (site / route).is_file(), f"missing {route}"


def test_every_public_page_becomes_exactly_one_html_file(site: Path) -> None:
    pages = load_public_pages(REPO_ROOT)
    for page in pages:
        parent = "frameworks" if page.category == "frameworks" else "about"
        assert (site / parent / page.slug / "index.html").is_file(), page.slug


def test_every_page_has_a_name_and_description() -> None:
    for page in load_public_pages(REPO_ROOT):
        assert page.name.strip(), f"{page.slug} has no name"
        assert page.description.strip(), f"{page.slug} has no description"


def test_search_index_matches_the_public_pages(site: Path) -> None:
    payload = json.loads((site / "search-index.json").read_text(encoding="utf-8"))
    assert len(payload) == len(load_public_pages(REPO_ROOT))
    for entry in payload:
        assert entry["name"]
        assert entry["path"].startswith(("/frameworks/", "/about/"))


def test_all_ten_safety_rules_are_rendered(site: Path) -> None:
    """Doctrine defines ten numbered rules, and the page shows all of them."""
    rules = load_safety_rules(REPO_ROOT)
    assert [rule.number for rule in rules] == list(range(1, 11))

    text = (site / "safety" / "index.html").read_text(encoding="utf-8")
    for rule in rules:
        assert rule.title in text


def test_safety_rule_bodies_are_not_truncated() -> None:
    """A rule's body carries its whole paragraph, not just its first line.

    Doctrine wraps its prose, so reading only the matched line cut every
    multi-line rule mid-sentence.
    """
    rules = {rule.number: rule for rule in load_safety_rules(REPO_ROOT)}
    assert rules[1].body.endswith(".")
    assert "signals safety" in rules[1].body
    assert rules[3].body.endswith(".")


def test_framework_tiers_come_from_doctrine() -> None:
    """Tiers are read from the SOULMAP.md table, never hardcoded."""
    tiers = load_priority_tiers(REPO_ROOT)
    assert tiers["crisis"] == "Highest"
    assert tiers["grief"] == "High"
    assert tiers["mirror"] == "Default"

    frameworks = [
        page for page in load_public_pages(REPO_ROOT) if page.category == "frameworks"
    ]
    assert any(page.tier == "High" for page in frameworks)
    # Most frameworks route, so an empty tier map would be a silent regression.
    assert sum(1 for page in frameworks if page.tier) >= 15


def test_untiered_frameworks_are_reported_not_dropped(site: Path) -> None:
    """A framework with no doctrine row still gets a page.

    Dropping it would hide a real doctrine gap behind a tidy index.
    """
    frameworks = [
        page for page in load_public_pages(REPO_ROOT) if page.category == "frameworks"
    ]
    untiered = [page for page in frameworks if page.tier is None]
    assert untiered, "expected at least one framework with no doctrine row"
    for page in untiered:
        assert (site / "frameworks" / page.slug / "index.html").is_file()


def test_links_to_private_files_are_flattened(tmp_path: Path) -> None:
    """A link into a private category renders as text, not a dead link."""
    source = tmp_path / "sample.md"
    source.write_text(
        '---\nname: "sample"\ndescription: "d"\n---\n\n'
        "# Sample\n\n"
        "See [skills/meta/master-prompt.md](../meta/master-prompt.md) for more.\n"
        "Also [the forbidden list](../safety/whitelist-blacklist-system.md).\n",
        encoding="utf-8",
    )
    page = build_page(source, tmp_path, {}, category="brand")
    html = " ".join(section.html for section in page.sections)

    assert "master-prompt" not in html
    assert "whitelist-blacklist" not in html
    assert "the forbidden list" in html


def test_internal_subsections_and_labelled_blocks_are_dropped(tmp_path: Path) -> None:
    """Signal content is removed whether it is a heading or a bold label.

    Both forms appear in the real knowledge base: `self-compassion.md` uses a
    level-3 heading and `pattern-mapper.md` uses six bold labels.
    """
    source = tmp_path / "sample.md"
    source.write_text(
        '---\nname: "sample"\ndescription: "d"\n---\n\n'
        "# Sample\n\n"
        "## Public section\n\nVisible prose.\n\n"
        "### Detection signals\n\n"
        '- "secret trigger phrase one"\n\n'
        "## Another public section\n\n"
        "**Detection signals:**\n\n"
        '- "secret trigger phrase two"\n\n'
        "Trailing visible prose.\n",
        encoding="utf-8",
    )
    page = build_page(source, tmp_path, {}, category="frameworks")
    html = " ".join(section.html for section in page.sections)

    assert "secret trigger phrase one" not in html
    assert "secret trigger phrase two" not in html
    assert "Visible prose." in html
    assert "Trailing visible prose." in html
