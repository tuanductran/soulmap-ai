from __future__ import annotations

import pytest

from web import pages
from web.i18n import SUPPORTED_LOCALES
from web.server import (
    _about,
    _boundaries,
    _download,
    _faq,
    _home,
    _how_it_works,
    _layout,
    _not_found,
    _notes,
    _privacy,
)


@pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
def test_public_page_renderers_keep_localized_layout_contract(locale: str) -> None:
    html = pages._layout(
        "Fallback title",
        "Fallback description",
        "/faq",
        pages._faq(locale),
        locale,
    )

    assert f'<html lang="{locale}">' in html
    assert '<main id="main-content">' in html
    assert '<script id="soulmap-locale-data" type="application/json">' in html
    assert 'rel="canonical"' in html
    assert 'hreflang="x-default"' in html
    assert "src/soulmap" not in html


@pytest.mark.parametrize(
    ("renderer", "marker"),
    [
        (pages._home, "home_h1"),
        (pages._how_it_works, "how_h1"),
        (pages._boundaries, "boundaries_h1"),
        (pages._download, "download_h1"),
        (pages._notes, "notes_h1"),
        (pages._about, "about_h1"),
        (pages._faq, "faq_h1"),
        (pages._privacy, "privacy_page_h1"),
        (pages._not_found, "not_found"),
    ],
)
def test_page_renderer_does_not_leak_i18n_keys(renderer: object, marker: str) -> None:
    html = renderer("en")  # type: ignore[operator]

    assert marker not in html
    assert "src/soulmap" not in html
    assert html


def test_server_keeps_page_renderer_compatibility_aliases() -> None:
    assert _home is pages._home
    assert _how_it_works is pages._how_it_works
    assert _boundaries is pages._boundaries
    assert _download is pages._download
    assert _notes is pages._notes
    assert _about is pages._about
    assert _faq is pages._faq
    assert _privacy is pages._privacy
    assert _not_found is pages._not_found
    assert _layout is pages._layout


def test_server_page_registry_remains_ordered_and_english_is_unprefixed() -> None:
    from web.server import _pages

    registry = _pages()
    assert list(registry) == [
        "/",
        "/how-it-works",
        "/boundaries",
        "/download",
        "/notes",
        "/about",
        "/faq",
        "/privacy",
        "/skills",
    ]
    assert registry["/"][2] is pages._home
    assert registry["/faq"][2] is pages._faq
