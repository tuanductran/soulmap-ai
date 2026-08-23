from pathlib import Path

from web.exporter import _apply_base_path, _normalise_base_path
from web.server import export_static


def test_normalise_base_path_handles_empty_root_and_project_prefixes() -> None:
    assert _normalise_base_path("") == ""
    assert _normalise_base_path("/") == ""
    assert _normalise_base_path("  /soulmap-ai/  ") == "/soulmap-ai"


def test_apply_base_path_rewrites_all_public_url_attributes_and_css() -> None:
    content = (
        '<a href="/faq" src="/image.svg" hx-get="/api/skills" '
        'action="/submit" data-search-api="/api/search" '
        'data-skill-root="/skills" data-detail-url="/partials/detail" '
        'style="background: url("/hero.svg")">content</a>'
    )

    rewritten = _apply_base_path(content, "/soulmap-ai")

    for attribute in (
        "href",
        "src",
        "hx-get",
        "action",
        "data-search-api",
        "data-skill-root",
        "data-detail-url",
    ):
        assert f'{attribute}="/soulmap-ai/' in rewritten
    assert 'url("/soulmap-ai/' in rewritten
    assert _apply_base_path(content, "") == content


def test_static_export_removes_stale_output_before_rebuilding(tmp_path: Path) -> None:
    output = tmp_path / "site"
    output.mkdir()
    stale = output / "stale.txt"
    stale.write_text("must be removed", encoding="utf-8")

    written = export_static(output)

    assert written
    assert not stale.exists()
    assert (output / "index.html").is_file()
