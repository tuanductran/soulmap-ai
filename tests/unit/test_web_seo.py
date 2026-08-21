import json

from soulmap.web.seo import alternate_links, json_ld, public_url, sitemap_xml

SITE = "https://tuanductran.github.io/soulmap-ai"
REPOSITORY = "https://github.com/tuanductran/soulmap-ai"


def test_public_url_uses_directory_style_canonical_paths() -> None:
    assert public_url(SITE, "/", "en") == f"{SITE}/"
    assert public_url(SITE, "/", "vi") == f"{SITE}/vi/"
    assert public_url(SITE, "/how-it-works", "en") == f"{SITE}/how-it-works/"
    assert public_url(SITE, "/how-it-works", "vi") == f"{SITE}/vi/how-it-works/"
    assert public_url(SITE, "/how-it-works", "ko") == f"{SITE}/ko/how-it-works/"


def test_alternate_links_are_reciprocal_and_include_x_default() -> None:
    links = alternate_links(SITE, "/faq")
    assert 'hreflang="en" href="https://tuanductran.github.io/soulmap-ai/faq/"' in links
    assert (
        'hreflang="vi" href="https://tuanductran.github.io/soulmap-ai/vi/faq/"' in links
    )
    assert (
        'hreflang="ko" href="https://tuanductran.github.io/soulmap-ai/ko/faq/"' in links
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


def test_json_ld_localizes_breadcrumb_labels_for_pages_and_skills() -> None:
    vietnamese = json.loads(
        json_ld(
            site_url=SITE,
            repository_url=REPOSITORY,
            canonical_url=f"{SITE}/vi/skills/meta/",
            locale="vi",
            title="Điều phối cốt lõi",
            description="Mô tả",
            route="/skills/meta",
        )
    )
    korean = json.loads(
        json_ld(
            site_url=SITE,
            repository_url=REPOSITORY,
            canonical_url=f"{SITE}/ko/how-it-works/",
            locale="ko",
            title="작동 방식",
            description="설명",
            route="/how-it-works",
        )
    )

    vi_names = [
        item["name"]
        for item in next(
            graph
            for graph in vietnamese["@graph"]
            if graph["@type"] == "BreadcrumbList"
        )["itemListElement"]
    ]
    ko_names = [
        item["name"]
        for item in next(
            graph for graph in korean["@graph"] if graph["@type"] == "BreadcrumbList"
        )["itemListElement"]
    ]
    assert vi_names == ["SoulMap AI", "Bộ Skills", "Điều phối cốt lõi"]
    assert ko_names == ["SoulMap AI", "작동 방식"]


def test_sitemap_contains_all_supported_locales_for_each_route() -> None:
    sitemap = sitemap_xml(SITE, ["/", "/privacy"])
    assert sitemap.count("<url>") == 6
    assert sitemap.count('hreflang="x-default"') == 6
    assert f"<loc>{SITE}/privacy/</loc>" in sitemap
    assert f"<loc>{SITE}/vi/privacy/</loc>" in sitemap
    assert f"<loc>{SITE}/ko/privacy/</loc>" in sitemap
    assert "api/" not in sitemap
