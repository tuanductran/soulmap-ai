from pathlib import Path

import pytest

from soulmap.web import templates
from soulmap.web.templates import render_template


def test_render_template_loads_checked_in_layout() -> None:
    rendered = render_template(
        "pages/not-found.html",
        not_found="Missing",
        not_found_body="Not here",
        home_href="/",
        return_home="Home",
    )

    assert '<p class="eyebrow">404</p>' in rendered
    assert "Missing" in rendered
    assert "Not here" in rendered


def test_render_template_reloads_when_source_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    template_path = tmp_path / "sample.html"
    template_path.write_text("<p>$value</p>", encoding="utf-8")
    monkeypatch.setattr(templates, "TEMPLATE_ROOT", tmp_path)

    assert templates.render_template("sample.html", value="first") == "<p>first</p>"

    template_path.write_text("<h1>$value changed</h1>", encoding="utf-8")

    assert templates.render_template("sample.html", value="second") == (
        "<h1>second changed</h1>"
    )


def test_render_template_is_strict_about_missing_values() -> None:
    with pytest.raises(KeyError, match="return_home"):
        render_template(
            "pages/not-found.html",
            not_found="Missing",
            not_found_body="Not here",
            home_href="/",
        )


def test_render_template_rejects_paths_outside_template_root() -> None:
    with pytest.raises(FileNotFoundError, match="template not found"):
        render_template("../server.py")
