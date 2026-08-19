"""SEO metadata and structured-data helpers for the static SoulMap website."""

from __future__ import annotations

import json
from html import escape
from typing import Any


def public_url(site_url: str, route: str, locale: str) -> str:
    """Return an absolute canonical public URL for a localized route."""
    normalized = route if route.startswith("/") else f"/{route}"
    prefix = "/vi" if locale == "vi" else ""
    suffix = "/" if normalized == "/" else f"{normalized}/"
    return f"{site_url.rstrip('/')}{prefix}{suffix}"


def alternate_links(site_url: str, route: str) -> str:
    """Render reciprocal EN/VI hreflang links plus an English x-default."""
    english = public_url(site_url, route, "en")
    vietnamese = public_url(site_url, route, "vi")
    return "\n".join(
        (
            f'<link rel="alternate" hreflang="en" href="{escape(english, quote=True)}">',
            f'<link rel="alternate" hreflang="vi" href="{escape(vietnamese, quote=True)}">',
            f'<link rel="alternate" hreflang="x-default" href="{escape(english, quote=True)}">',
        )
    )


def _safe_json(value: Any) -> str:
    """Serialize JSON for HTML script text without allowing markup termination."""
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def json_ld(
    *,
    site_url: str,
    repository_url: str,
    canonical_url: str,
    locale: str,
    title: str,
    description: str,
    route: str,
) -> str:
    """Build truthful server-rendered Organization, WebSite, WebPage and breadcrumbs."""
    website_url = f"{site_url.rstrip('/')}/"
    organization_id = f"{website_url}#organization"
    website_id = f"{website_url}#website"
    page_id = f"{canonical_url}#webpage"
    graph: list[dict[str, Any]] = [
        {
            "@type": "Organization",
            "@id": organization_id,
            "name": "SoulMap AI",
            "url": website_url,
            "sameAs": [repository_url],
        },
        {
            "@type": "WebSite",
            "@id": website_id,
            "url": website_url,
            "name": "SoulMap AI",
            "publisher": {"@id": organization_id},
        },
        {
            "@type": "WebPage",
            "@id": page_id,
            "url": canonical_url,
            "name": title,
            "description": description,
            "inLanguage": locale,
            "isPartOf": {"@id": website_id},
            "about": {"@id": organization_id},
        },
    ]
    if route != "/":
        segments = [segment for segment in route.strip("/").split("/") if segment]
        labels = ["SoulMap AI", *segments]
        items: list[dict[str, Any]] = []
        for position, label in enumerate(labels, 1):
            item_route = (
                "/" if position == 1 else "/" + "/".join(segments[: position - 1])
            )
            item: dict[str, Any] = {
                "@type": "ListItem",
                "position": position,
                "name": label.replace("-", " ").title(),
            }
            if position < len(labels):
                item["item"] = public_url(site_url, item_route, locale)
            items.append(item)
        graph.append(
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": items,
            }
        )
    return _safe_json({"@context": "https://schema.org", "@graph": graph})


def metadata(
    *,
    site_url: str,
    repository_url: str,
    route: str,
    locale: str,
    title: str,
    description: str,
) -> dict[str, str]:
    """Return escaped layout values for canonical, social and JSON-LD metadata."""
    canonical = public_url(site_url, route, locale)
    escaped_title = escape(title, quote=True)
    escaped_description = escape(description, quote=True)
    return {
        "canonical_url": escape(canonical, quote=True),
        "alternate_links": alternate_links(site_url, route),
        "og_title": escaped_title,
        "og_description": escaped_description,
        "og_url": escape(canonical, quote=True),
        "og_locale": "vi_VN" if locale == "vi" else "en_US",
        "og_locale_alternate": "en_US" if locale == "vi" else "vi_VN",
        "json_ld": json_ld(
            site_url=site_url,
            repository_url=repository_url,
            canonical_url=canonical,
            locale=locale,
            title=title,
            description=description,
            route=route,
        ),
    }


def sitemap_xml(site_url: str, routes: list[str]) -> str:
    """Render a small XML sitemap with reciprocal EN/VI alternate links."""
    from xml.sax.saxutils import escape as xml_escape

    entries: list[str] = []
    for route in routes:
        alternates = {
            "en": public_url(site_url, route, "en"),
            "vi": public_url(site_url, route, "vi"),
        }
        for _locale, canonical in alternates.items():
            links = "".join(
                f'<xhtml:link rel="alternate" hreflang="{language}" href="{xml_escape(url)}" />'
                for language, url in (
                    *alternates.items(),
                    ("x-default", alternates["en"]),
                )
            )
            entries.append(
                f"  <url>\n    <loc>{xml_escape(canonical)}</loc>\n{links}\n  </url>"
            )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def robots_txt(site_url: str) -> str:
    """Render the public crawler policy and canonical sitemap location."""
    return f"User-agent: *\nAllow: /\n\nSitemap: {site_url.rstrip('/')}/sitemap.xml\n"
