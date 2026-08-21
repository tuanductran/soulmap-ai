"""Static export orchestration for the public SoulMap website."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path

from soulmap.web.assets import STATIC_DIR
from soulmap.web.build import build_key, load_reusable_output, write_manifest
from soulmap.web.catalog import (
    CATALOG,
    catalog_json,
    catalog_search_json,
    locale_fields,
    raw_markdown,
    raw_path,
    raw_url,
)
from soulmap.web.i18n import SUPPORTED_LOCALES
from soulmap.web.prompt_pack import scenarios_for
from soulmap.web.seo import robots_txt, sitemap_xml

PUBLIC_SITE_URL = "https://tuanductran.github.io/soulmap-ai"
PageRenderer = Callable[[str], str]
PagesFactory = Callable[[], dict[str, tuple[str, str, PageRenderer]]]
SkillRenderer = Callable[[str, str], str]
FragmentRenderer = Callable[[str, str], str]
GridRenderer = Callable[[str], str]
StaticCssReader = Callable[[], str]
SitemapRoutes = Callable[[], list[str]]
LayoutRenderer = Callable[[str, str, str, str, str], str]


def _normalise_base_path(base_path: str) -> str:
    cleaned = base_path.strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def _apply_base_path(content: str, base_path: str) -> str:
    if not base_path:
        return content
    for attribute in (
        "href",
        "src",
        "hx-get",
        "action",
        "data-search-api",
        "data-skill-root",
    ):
        content = content.replace(f'{attribute}="/', f'{attribute}="{base_path}/')
    return content.replace('url("/', f'url("{base_path}/')


def _write_page(
    output: Path, route: str, page: str, written: list[Path], base_path: str
) -> None:
    destination = output / ("index.html" if route == "/" else route.strip("/"))
    destination = destination if destination.suffix else destination / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(_apply_base_path(page, base_path), encoding="utf-8")
    written.append(destination)


def export_static(
    output: Path,
    base_path: str = "",
    *,
    pages_factory: PagesFactory,
    skill_page_renderer: SkillRenderer,
    skill_detail_renderer: FragmentRenderer,
    skill_grid_renderer: GridRenderer,
    static_css_reader: StaticCssReader,
    sitemap_routes: SitemapRoutes,
    page_layout: LayoutRenderer,
    incremental: bool = False,
    cache_dir: Path | None = None,
) -> list[Path]:
    """Export public pages, APIs and bundles, optionally reusing a verified build."""
    output = output.resolve()
    normalised_base = _normalise_base_path(base_path)
    build_cache = (
        cache_dir or output.parent / f".{output.name}.soulmap-build"
    ).resolve()
    key = build_key(normalised_base)
    if incremental:
        reusable = load_reusable_output(build_cache, output, key)
        if reusable is not None:
            return reusable
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    written: list[Path] = []
    pages = pages_factory()
    for locale in SUPPORTED_LOCALES:
        locale_prefix = "" if locale == "en" else f"/{locale}"
        for route, (title, description, renderer) in pages.items():
            page_route = f"{locale_prefix}{route if route != '/' else ''}" or "/"
            _write_page(
                output,
                page_route,
                page_layout(
                    title,
                    description,
                    route,
                    renderer(locale),
                    locale,
                ),
                written,
                normalised_base,
            )
    for entry in CATALOG:
        for locale in SUPPORTED_LOCALES:
            prefix = "" if locale == "en" else f"/{locale}"
            _write_page(
                output,
                f"{prefix}/skills/{entry.slug}",
                page_layout(
                    locale_fields(entry, locale)["title"],
                    locale_fields(entry, locale)["summary"],
                    f"/skills/{entry.slug}",
                    skill_page_renderer(entry.slug, locale),
                    locale,
                ),
                written,
                normalised_base,
            )
            partial = output / f"partials/skill/{entry.slug}.{locale}.html"
            partial.parent.mkdir(parents=True, exist_ok=True)
            partial.write_text(
                _apply_base_path(
                    skill_detail_renderer(entry.slug, locale), normalised_base
                ),
                encoding="utf-8",
            )
            written.append(partial)
    for locale in SUPPORTED_LOCALES:
        grid_partial = output / (
            "partials/skills-grid.html"
            if locale == "en"
            else f"{locale}/partials/skills-grid.html"
        )
        grid_partial.parent.mkdir(parents=True, exist_ok=True)
        grid_partial.write_text(
            _apply_base_path(skill_grid_renderer(locale), normalised_base),
            encoding="utf-8",
        )
        written.append(grid_partial)
    api_dir = output / "api"
    (api_dir / "raw").mkdir(parents=True, exist_ok=True)
    (api_dir / "skills").mkdir(parents=True, exist_ok=True)
    (api_dir / "skills.json").write_text(catalog_json(), encoding="utf-8")
    (api_dir / "skills" / "search.json").write_text(
        catalog_search_json(), encoding="utf-8"
    )
    written.extend([api_dir / "skills.json", api_dir / "skills" / "search.json"])
    for locale in SUPPORTED_LOCALES:
        if locale == "en":
            continue
        locale_api_dir = output / locale / "api" / "skills"
        locale_api_dir.mkdir(parents=True, exist_ok=True)
        locale_api_json = output / locale / "api" / "skills.json"
        locale_api_json.write_text(catalog_json(locale), encoding="utf-8")
        locale_search_json = locale_api_dir / "search.json"
        locale_search_json.write_text(catalog_search_json(locale), encoding="utf-8")
        written.extend([locale_api_json, locale_search_json])
    for entry in CATALOG:
        english_raw_path = api_dir / "raw" / f"{entry.slug}.md"
        english_raw_path.write_text(raw_markdown(entry), encoding="utf-8")
        written.append(english_raw_path)
        data_path = api_dir / "skills" / f"{entry.slug}.json"
        data_path.write_text(
            json.dumps(entry.public_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written.append(data_path)
        prompt_dir = api_dir / "skills" / entry.slug
        prompt_dir.mkdir(parents=True, exist_ok=True)
        for prompt_locale in SUPPORTED_LOCALES:
            prompt_path = prompt_dir / (
                "prompts.json"
                if prompt_locale == "en"
                else f"prompts.{prompt_locale}.json"
            )
            prompt_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "locale": prompt_locale,
                        "slug": entry.slug,
                        "raw_url": raw_url(entry.slug, prompt_locale),
                        "scenarios": [
                            scenario.localized(prompt_locale)
                            for scenario in scenarios_for(entry.slug)
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            written.append(prompt_path)
            if prompt_locale == "en":
                continue
            localized_raw_path = output / raw_path(entry.slug, prompt_locale).lstrip(
                "/"
            )
            localized_raw_path.parent.mkdir(parents=True, exist_ok=True)
            localized_raw_path.write_text(
                raw_markdown(entry, prompt_locale), encoding="utf-8"
            )
            written.append(localized_raw_path)
            localized_data_path = (
                output / prompt_locale / "api" / "skills" / f"{entry.slug}.json"
            )
            localized_data_path.parent.mkdir(parents=True, exist_ok=True)
            localized_data_path.write_text(
                json.dumps(
                    entry.public_dict(prompt_locale), ensure_ascii=False, indent=2
                ),
                encoding="utf-8",
            )
            written.append(localized_data_path)
            localized_prompt_path = (
                output / prompt_locale / "api" / "skills" / entry.slug / "prompts.json"
            )
            localized_prompt_path.parent.mkdir(parents=True, exist_ok=True)
            localized_prompt_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "locale": prompt_locale,
                        "slug": entry.slug,
                        "raw_url": raw_url(entry.slug, prompt_locale),
                        "scenarios": [
                            scenario.localized(prompt_locale)
                            for scenario in scenarios_for(entry.slug)
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            written.append(localized_prompt_path)
    (output / "static").mkdir()
    (output / "static" / "site.css").write_text(
        _apply_base_path(static_css_reader(), normalised_base), encoding="utf-8"
    )
    for asset_name in ("site.js", "search.js"):
        (output / "static" / asset_name).write_text(
            (STATIC_DIR / asset_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    fonts_output = output / "static" / "fonts"
    fonts_output.mkdir(parents=True, exist_ok=True)
    for font_name in ("InterVariable.woff2", "ManropeVariable.woff2"):
        font_path = fonts_output / font_name
        shutil.copyfile(STATIC_DIR / "fonts" / font_name, font_path)
    favicon_source = STATIC_DIR / "favicon.ico"
    shutil.copyfile(favicon_source, output / "favicon.ico")
    (output / "robots.txt").write_text(robots_txt(PUBLIC_SITE_URL), encoding="utf-8")
    (output / "sitemap.xml").write_text(
        sitemap_xml(PUBLIC_SITE_URL, sitemap_routes()), encoding="utf-8"
    )
    written.extend(
        [
            output / "static" / "site.css",
            output / "static" / "site.js",
            output / "static" / "search.js",
            output / "static" / "fonts" / "InterVariable.woff2",
            output / "static" / "fonts" / "ManropeVariable.woff2",
            output / "favicon.ico",
            output / "robots.txt",
            output / "sitemap.xml",
        ]
    )
    if incremental:
        write_manifest(build_cache, output, key, written)
    return written
