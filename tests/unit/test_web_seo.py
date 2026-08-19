import json

from soulmap.web.seo import alternate_links, json_ld, public_url, sitemap_xml

SITE = "https://tuanductran.github.io/soulmap-ai"
REPOSITORY = "https://github.com/tuanductran/soulmap-ai"


def test_public_url_uses_directory_style_canonical_paths() -> None:
    assert public_url(SITE, "/", "en") == f"{SITE}/"
    assert public_url(SITE, "/", "vi") == f"{SITE}/vi/"
    assert public_url(SITE, "/how-it-works", "en") == f"{SITE}/how-it-works/"
    assert public_url(SITE, "/how-it-works", "vi") == f"{SITE}/vi/how-it-works/"


def test_alternate_links_are_reciprocal_and_include_x_default() -> None:
    links = alternate_links(SITE, "/faq")
    assert 'hreflang="en" href="https://tuanductran.github.io/soulmap-ai/faq/"' in links
    assert (
        'hreflang="vi" href="https://tuanductran.github.io/soulmap-ai/vi/faq/"' in links
    )
    assert (
        'hreflang="x-default" href="https://tuanductran.github.io/soulmap-ai/faq/"'
        in links
    )


def test_json_ld_is_valid_and_escapes_script_terminators() -> None:
    payload = json.loads(
        json_ld(
            site_url=SITE,
            repository_url=REPOSITORY,
            canonical_url=f"{SITE}/faq/",
            locale="en",
            title="Question </script>",
            description="Description & detail",
            route="/faq",
        )
    )
    assert payload["@context"] == "https://schema.org"
    assert any(item["@type"] == "Organization" for item in payload["@graph"])
    assert "</script>" not in json_ld(
        site_url=SITE,
        repository_url=REPOSITORY,
        canonical_url=f"{SITE}/faq/",
        locale="en",
        title="Question </script>",
        description="Description & detail",
        route="/faq",
    )


def test_sitemap_contains_both_locales_for_each_route() -> None:
    sitemap = sitemap_xml(SITE, ["/", "/privacy"])
    assert sitemap.count("<url>") == 4
    assert sitemap.count('hreflang="x-default"') == 4
    assert f"<loc>{SITE}/privacy/</loc>" in sitemap
    assert f"<loc>{SITE}/vi/privacy/</loc>" in sitemap
    assert "api/" not in sitemap
