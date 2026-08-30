"""Boundary tests for the public website.

These are the tests that matter most in this package. They assert on the bytes
the build would actually publish, not on the allowlist's intent, because the
allowlist and the loader are both code that can be wrong.

Each test here was checked against the repository's revert-and-confirm-red
standard: the exclusion it protects was temporarily disabled, the test was
watched to fail, and the exclusion was restored. A boundary test that cannot
fail is the bug class `docs/engineering/TESTER.md` Charter 5 names.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.devtools.web.allowlist import is_internal_section, is_public_skill
from soulmap.devtools.web.build import build_site
from soulmap.devtools.web.guard import check_output

# Files whose publication would breach doctrine or expose the safety layer.
# Each is named in docs/web/CONTENT-MODEL.md with its reason.
FORBIDDEN_FILES = (
    ("meta", "master-prompt.md"),
    ("meta", "redirect-templates.md"),
    ("meta", "deep-inquiry-bank.md"),
    ("meta", "framework-template-map.md"),
    ("safety", "boundaries-safety.md"),
    ("safety", "whitelist-blacklist-system.md"),
    ("safety", "prompt-injection-defense.md"),
    ("spiritual", "founder-numerology.md"),
    ("spiritual", "numerology-profile.md"),
    ("brand", "founder-personal-brand.md"),
    ("brand", "strategic-direction-2026.md"),
)


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the site once for every test in this module."""
    output = tmp_path_factory.mktemp("site") / "site"
    build_site(output)
    return output


def test_generated_output_has_no_boundary_leaks(site: Path) -> None:
    """The guard finds nothing in a real build of the real repository."""
    leaks = check_output(site, repo_root=REPO_ROOT)
    assert not leaks, "\n".join(
        f"{leak.path.name}: {leak.kind}: {leak.detail}" for leak in leaks
    )


@pytest.mark.parametrize(("category", "filename"), FORBIDDEN_FILES)
def test_forbidden_file_is_not_published(category: str, filename: str) -> None:
    """Each file the content model excludes stays excluded by the allowlist."""
    assert not is_public_skill(category, filename)


def test_forbidden_file_content_is_absent_from_output(site: Path) -> None:
    """No excluded file's distinctive content appears anywhere in the build.

    This checks the output rather than the allowlist, so a loader that ignored
    the allowlist would still be caught.
    """
    rendered = " ".join(
        path.read_text(encoding="utf-8") for path in site.rglob("*.html")
    )

    for category, filename in FORBIDDEN_FILES:
        source = REPO_ROOT / "skills" / category / filename
        if not source.is_file():
            continue
        # The first substantial prose line is distinctive enough to identify
        # the file, and stable enough not to make the test brittle.
        for line in source.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if len(stripped) > 60 and not stripped.startswith(("#", "-", "|", ">")):
                assert stripped not in rendered, (
                    f"content from {category}/{filename} reached the site"
                )
                break


def test_no_internal_section_headings_are_rendered(site: Path) -> None:
    """No page renders a detection, activation, or paired-template heading."""
    offenders: list[str] = []
    for path in sorted(site.rglob("*.html")):
        text = path.read_text(encoding="utf-8").lower()
        for heading in ("detection signals", "activation signals", "paired template"):
            if re.search(rf"<h[1-6][^>]*>\s*{re.escape(heading)}", text):
                offenders.append(f"{path.name}: {heading}")
    assert not offenders, offenders


def test_skill_entry_points_are_never_public() -> None:
    """A category's own SKILL.md is agent routing guidance, never a page."""
    for category in ("frameworks", "brand", "voice", "meta", "safety"):
        assert not is_public_skill(category, "SKILL.md")


def test_private_categories_publish_nothing() -> None:
    """No file from a private category is publishable, listed or not."""
    for category in ("meta", "safety", "spiritual", "soulmate"):
        assert not is_public_skill(category, "anything.md")
        assert not is_public_skill(category, "SKILL.md")


def test_internal_section_matching_ignores_case_and_spacing() -> None:
    """Section matching is not defeated by casing or surrounding whitespace."""
    assert is_internal_section("Detection signals")
    assert is_internal_section("  ACTIVATION SIGNALS  ")
    assert is_internal_section("Paired template")
    assert not is_internal_section("The core stance")


def test_every_public_page_links_back_to_its_source(site: Path) -> None:
    """Framework pages cite the repository file they were generated from."""
    for path in sorted((site / "frameworks").glob("*/index.html")):
        text = path.read_text(encoding="utf-8")
        assert "skills/frameworks/" in text, f"{path.name} has no source link"
