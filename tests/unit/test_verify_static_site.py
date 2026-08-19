from pathlib import Path

import pytest

from scripts.verify_static_site import _validate_script_tag


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
