"""Build the static SoulMap website.

Reads canonical repository files, renders them through Jinja2 templates, and
writes static HTML into an output directory. The build is one-directional: it
never writes to `skills/`, never imports `soulmap.runtime`, and never starts a
server.

`--check` runs the same build into a temporary directory and asserts the
public-content boundaries, so CI catches a change that would publish an
unlisted document without needing to publish anything.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.devtools.web.content import PublicPage, load_public_pages
from soulmap.devtools.web.doctrine import (
    PriorityTier,
    load_safety_rules,
    priority_tiers,
)
from soulmap.devtools.web.guard import Leak, check_output

SITE_URL = "https://soulmap-ai.pages.dev/"
REPO_URL = "https://github.com/tuanductran/soulmap-ai"
REPO_BLOB = f"{REPO_URL}/blob/main"

SITE_TITLE = "SoulMap AI"
SITE_DESCRIPTION = (
    "SoulMap is a reflective companion that helps people hear themselves more "
    "clearly. It does not advise, diagnose, or predict."
)


@dataclass(frozen=True, slots=True)
class BuildReport:
    """The outcome of one build.

    Attributes:
        pages_written: Number of HTML files written.
        frameworks: Number of public framework pages.
        untiered: Framework slugs with no row in the doctrine priority table.
            Not a defect. The table ranks primary frameworks, and these are
            applied alongside one (anger and somatic are secondary layers on a
            de-escalation selection; others are topic lenses). See
            `tests/contract/test_priority_hierarchy_contract.py`, which fails if
            a genuinely primary-routed framework ever goes unranked.
    """

    pages_written: int
    frameworks: int
    untiered: tuple[str, ...]


def _environment(website_root: Path) -> Environment:
    """Build the Jinja2 environment used for every page.

    Args:
        website_root: The `website/` directory holding `templates/`.

    Returns:
        An environment with autoescaping on and undefined names raising.
        `StrictUndefined` matters here: a typo in a template variable should
        fail the build rather than silently render an empty page.
    """
    return Environment(
        loader=FileSystemLoader(website_root / "templates"),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _write(destination: Path, html: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")


def _base_context(*, title: str, description: str, path: str, section: str) -> dict:
    return {
        "page_title": title,
        "page_description": description,
        "page_path": path,
        "section": section,
        "site_url": SITE_URL,
        "repo_url": REPO_URL,
        "repo_blob": REPO_BLOB,
    }


def _group_by_tier(
    pages: list[PublicPage], tiers: list[PriorityTier]
) -> list[dict[str, object]]:
    """Group framework pages under their doctrine priority tier.

    A framework with no doctrine row is not dropped. It is collected into a
    trailing "supporting" group, which is the accurate description: the
    priority table ranks primary frameworks, and these are applied alongside
    one rather than routed on their own.

    Args:
        pages: Public framework pages.
        tiers: Ordered tiers in use.

    Returns:
        Template-ready groups in priority order.
    """
    groups: list[dict[str, object]] = []
    for tier in tiers:
        members = [page for page in pages if page.tier == tier.label]
        if members:
            groups.append(
                {
                    "label": tier.label,
                    "slug": tier.slug,
                    "note": tier.note,
                    "pages": sorted(members, key=lambda page: page.name),
                }
            )

    untiered = [page for page in pages if page.tier is None]
    if untiered:
        groups.append(
            {
                "label": "Supporting",
                "slug": "supporting",
                "note": "Applied alongside a primary framework rather than routed on their own",
                "pages": sorted(untiered, key=lambda page: page.name),
            }
        )
    return groups


def build_site(output: Path, *, repo_root: Path = REPO_ROOT) -> BuildReport:
    """Generate the complete static site.

    Args:
        output: Directory to write into. Replaced if it already exists.
        repo_root: Repository root.

    Returns:
        A report describing what was written.

    Raises:
        OSError: If a canonical file cannot be read or the output cannot be
            written.
    """
    website_root = repo_root / "website"
    env = _environment(website_root)
    pages = load_public_pages(repo_root)

    frameworks = [page for page in pages if page.category == "frameworks"]
    about_pages = [page for page in pages if page.category in {"brand", "voice"}]
    tiers = priority_tiers({page.tier for page in frameworks if page.tier})
    groups = _group_by_tier(frameworks, tiers)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    written = 0

    context = _base_context(
        title=f"{SITE_TITLE}, a reflective companion",
        description=SITE_DESCRIPTION,
        path="",
        section="home",
    )
    context["framework_count"] = len(frameworks)
    _write(output / "index.html", env.get_template("index.html").render(**context))
    written += 1

    context = _base_context(
        title=f"Frameworks, {SITE_TITLE}",
        description=(
            "The reflective frameworks SoulMap routes between, in the priority "
            "order it actually applies."
        ),
        path="frameworks/",
        section="frameworks",
    )
    context["tiers"] = groups
    _write(
        output / "frameworks" / "index.html",
        env.get_template("frameworks.html").render(**context),
    )
    written += 1

    template = env.get_template("framework.html")
    for page in frameworks:
        context = _base_context(
            title=f"{page.name}, {SITE_TITLE}",
            description=page.description or SITE_DESCRIPTION,
            path=f"frameworks/{page.slug}/",
            section="frameworks",
        )
        context["page"] = page
        _write(
            output / "frameworks" / page.slug / "index.html", template.render(**context)
        )
        written += 1

    context = _base_context(
        title=f"Safety, {SITE_TITLE}",
        description=(
            "The ten non-negotiable safety rules SoulMap enforces, as written in "
            "its own doctrine."
        ),
        path="safety/",
        section="safety",
    )
    context["rules"] = load_safety_rules(repo_root)
    _write(
        output / "safety" / "index.html",
        env.get_template("safety.html").render(**context),
    )
    written += 1

    context = _base_context(
        title=f"Architecture, {SITE_TITLE}",
        description=(
            "How SoulMap routes a message deterministically and validates the "
            "response before it reaches the reader."
        ),
        path="architecture/",
        section="architecture",
    )
    context["tiers"] = tiers
    _write(
        output / "architecture" / "index.html",
        env.get_template("architecture.html").render(**context),
    )
    written += 1

    context = _base_context(
        title=f"About, {SITE_TITLE}",
        description="What SoulMap is for, and what it refuses to become.",
        path="about/",
        section="about",
    )
    context["pages"] = sorted(about_pages, key=lambda page: page.name)
    _write(
        output / "about" / "index.html",
        env.get_template("about.html").render(**context),
    )
    written += 1

    template = env.get_template("document.html")
    for page in about_pages:
        context = _base_context(
            title=f"{page.name}, {SITE_TITLE}",
            description=page.description or SITE_DESCRIPTION,
            path=f"about/{page.slug}/",
            section="about",
        )
        context["page"] = page
        context["parent_path"] = "about"
        context["parent_label"] = "About"
        _write(output / "about" / page.slug / "index.html", template.render(**context))
        written += 1

    context = _base_context(
        title=f"Page not found, {SITE_TITLE}",
        description="That page does not exist.",
        path="404.html",
        section="none",
    )
    _write(output / "404.html", env.get_template("404.html").render(**context))
    written += 1

    _write_assets(website_root, output)
    _write_index_json(output, pages)
    _write_sitemap(output, pages, about_pages, frameworks)
    _write_robots(output)

    return BuildReport(
        pages_written=written,
        frameworks=len(frameworks),
        untiered=tuple(sorted(p.slug for p in frameworks if p.tier is None)),
    )


def _write_assets(website_root: Path, output: Path) -> None:
    static_root = website_root / "static"
    for asset in sorted(static_root.iterdir()):
        if asset.is_file():
            shutil.copy2(asset, output / asset.name)


def _write_index_json(output: Path, pages: list[PublicPage]) -> None:
    """Write the search index consumed by the client filter."""
    payload = [
        {
            "name": page.name,
            "description": page.description,
            "category": page.category,
            "tier": page.tier,
            "path": (
                f"/frameworks/{page.slug}/"
                if page.category == "frameworks"
                else f"/about/{page.slug}/"
            ),
        }
        for page in pages
    ]
    _write(
        output / "search-index.json",
        json.dumps(payload, ensure_ascii=False, indent=2),
    )


def _write_sitemap(
    output: Path,
    pages: list[PublicPage],
    about_pages: list[PublicPage],
    frameworks: list[PublicPage],
) -> None:
    paths = ["", "frameworks/", "safety/", "architecture/", "about/"]
    paths += [f"frameworks/{page.slug}/" for page in frameworks]
    paths += [f"about/{page.slug}/" for page in about_pages]

    entries = "\n".join(f"  <url><loc>{SITE_URL}{path}</loc></url>" for path in paths)
    _write(
        output / "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n",
    )


def _write_robots(output: Path) -> None:
    _write(
        output / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n",
    )


def main(argv: list[str] | None = None) -> int:
    """Run the website build from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 on success, 1 when a boundary check fails.
    """
    parser = argparse.ArgumentParser(prog="soulmap build-site")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "dist" / "site",
        help="Directory to write the site into (default: dist/site).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build into a temporary directory and verify content boundaries.",
    )
    args = parser.parse_args(argv)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / "site"
            report = build_site(site)
            leaks = check_output(site, repo_root=REPO_ROOT)
            print(
                f"build-site check: {report.pages_written} pages, "
                f"{report.frameworks} frameworks"
            )
            if report.untiered:
                print(
                    "  supporting (not primary-routed): " + ", ".join(report.untiered)
                )
            if leaks:
                return _report_leaks(leaks)
            print("  public-content boundary: clean")
        return 0

    report = build_site(args.output)
    leaks = check_output(args.output, repo_root=REPO_ROOT)
    if leaks:
        # Remove the output rather than leaving a directory that looks
        # publishable but is not.
        shutil.rmtree(args.output, ignore_errors=True)
        return _report_leaks(leaks)

    print(f"Wrote {report.pages_written} pages to {args.output}")
    if report.untiered:
        print("  supporting (not primary-routed): " + ", ".join(report.untiered))
    return 0


def _report_leaks(leaks: list[Leak]) -> int:
    """Print every leak found and return a failing exit code.

    Args:
        leaks: Leaks from ``check_output``.

    Returns:
        Always 1. A leak is never a warning.
    """
    print(f"\nBLOCKED: {len(leaks)} public-content boundary violations")
    for leak in leaks[:40]:
        print(f"  {leak.path.name}: {leak.kind}: {leak.detail}")
    if len(leaks) > 40:
        print(f"  ... and {len(leaks) - 40} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
