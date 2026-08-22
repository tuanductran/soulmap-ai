from soulmap.web.assets import (
    read_font_asset,
    read_text_asset,
    static_asset_type,
)


def test_asset_readers_fail_closed_for_unknown_names() -> None:
    assert read_text_asset("unknown.js") is None
    assert read_font_asset("unknown.woff2") is None
    assert static_asset_type("unknown.asset") is None


def test_asset_types_cover_text_and_font_allow_lists() -> None:
    assert static_asset_type("site.css") == "text/css"
    assert static_asset_type("site.js") == "text/javascript"
    assert static_asset_type("InterVariable.woff2") == "font/woff2"
