from pathlib import Path

import pytest

from scripts.verify_static_site import (
    _validate_local_link_targets,
    _validate_script_tag,
)


def test_local_link_targets_accept_directory_index_and_query(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("", encoding="utf-8")
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "index.html").write_text("", encoding="utf-8")
    (tmp_path / "partials").mkdir()
    (tmp_path / "partials" / "skills-grid.html").write_text("", encoding="utf-8")
    content = (
        '<a href="/soulmap-ai/">home</a>'
        '<a href="/soulmap-ai/skills">skills</a>'
        '<div hx-get="/soulmap-ai/partials/skills-grid.html?q=spiritual"></div>'
    )
    _validate_local_link_targets(content, "/soulmap-ai", tmp_path, Path("index.html"))


def test_local_link_targets_reject_missing_artifact(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing local target"):
        _validate_local_link_targets(
            '<a href="/soulmap-ai/missing">missing</a>',
            "/soulmap-ai",
            tmp_path,
            Path("index.html"),
        )


def test_local_link_targets_validate_form_action_and_search_api(tmp_path: Path) -> None:
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "index.html").write_text("", encoding="utf-8")
    (tmp_path / "api" / "skills").mkdir(parents=True)
    (tmp_path / "api" / "skills" / "search.json").write_text("{}", encoding="utf-8")
    _validate_local_link_targets(
        '<form action="/soulmap-ai/skills"></form>'
        '<form data-search-api="/soulmap-ai/api/skills/search.json"></form>',
        "/soulmap-ai",
        tmp_path,
        Path("skills/index.html"),
    )


def test_local_link_targets_reject_missing_search_api(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing local target"):
        _validate_local_link_targets(
            '<form data-search-api="/soulmap-ai/api/skills/missing.json"></form>',
            "/soulmap-ai",
            tmp_path,
            Path("skills/index.html"),
        )


@pytest.mark.parametrize(
    "script_tag",
    [
        '<SCRIPT SRC="https://cdn.jsdelivr.net/npm/example.js" INTEGRITY="sha384-test">',
        '<script src="https://cdn.jsdelivr.net/npm/example.js" integrity="sha384-test">',
    ],
)
def test_script_validation_is_case_insensitive(script_tag: str) -> None:
    _validate_script_tag(script_tag, "", Path("index.html"))


@pytest.mark.parametrize(
    "script_src",
    [
        "https://cdn.jsdelivr.net.evil.example/example.js",
        "https://cdn.jsdelivr.net@evil.example/example.js",
        "https://cdn.jsdelivr.net:8443/example.js",
        "//cdn.jsdelivr.net/npm/example.js",
    ],
)
def test_script_validation_rejects_ambiguous_external_urls(script_src: str) -> None:
    with pytest.raises(ValueError, match="unapproved external script"):
        _validate_script_tag(
            f'<script src="{script_src}" integrity="sha384-test">',
            "",
            Path("index.html"),
        )


def test_script_validation_requires_sri_for_allowed_external_url() -> None:
    with pytest.raises(ValueError, match="missing SRI"):
        _validate_script_tag(
            '<script src="https://cdn.jsdelivr.net/npm/example.js">',
            "",
            Path("index.html"),
        )
