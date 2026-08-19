"""Validate the generated static SoulMap website before publication."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EXPECTED_FILES = {
    "index.html",
    "how-it-works/index.html",
    "boundaries/index.html",
    "download/index.html",
    "notes/index.html",
    "about/index.html",
    "static/site.css",
    "robots.txt",
}
FORBIDDEN_FILE_PARTS = {
    ".claude",
    ".github",
    ".git",
    "dist",
    "skills",
    "src",
    "tests",
}
FORBIDDEN_SUFFIXES = {".py", ".md", ".toml", ".lock"}


def _normalise_base_path(base_path: str) -> str:
    cleaned = base_path.strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def verify_static_site(root: Path, base_path: str = "") -> None:
    """Raise ``ValueError`` when ``root`` is not a safe static site directory."""
    root = root.resolve()
    normalised_base = _normalise_base_path(base_path)
    if not root.is_dir():
        raise ValueError(f"static site directory does not exist: {root}")

    files = {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }
    missing = EXPECTED_FILES - files
    if missing:
        raise ValueError(f"missing static site files: {sorted(missing)}")

    unexpected = files - EXPECTED_FILES
    if unexpected:
        raise ValueError(f"unexpected static site files: {sorted(unexpected)}")

    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(
                f"static site must not contain symlinks: {path.relative_to(root)}"
            )
        relative = path.relative_to(root)
        if any(part in FORBIDDEN_FILE_PARTS for part in relative.parts):
            raise ValueError(f"static site contains forbidden path: {relative}")
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            raise ValueError(f"static site contains source file: {relative}")

    for html_path in sorted(root.rglob("*.html")):
        content = html_path.read_text(encoding="utf-8")
        required_markers = ('<html lang="en">', 'name="viewport"', 'id="main-content"')
        missing_markers = [
            marker for marker in required_markers if marker not in content
        ]
        if missing_markers:
            raise ValueError(
                f"{html_path.relative_to(root)} missing markers: {missing_markers}"
            )
        if "<script" in content.lower():
            raise ValueError(
                f"static HTML must not load scripts: {html_path.relative_to(root)}"
            )
        if normalised_base:
            links = re.findall(r'href="(/[^\"]*)"', content)
            invalid_links = [
                link for link in links if not link.startswith(normalised_base + "/")
            ]
            if invalid_links:
                raise ValueError(
                    f"static HTML contains links outside base path in {html_path.relative_to(root)}: {invalid_links}"
                )
        if "127.0.0.1" in content or "localhost" in content:
            raise ValueError(
                f"static HTML contains local development host: {html_path.relative_to(root)}"
            )


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a generated SoulMap static site."
    )
    parser.add_argument("root", type=Path, help="Static site directory to verify.")
    parser.add_argument(
        "--base-path", default="", help="Expected GitHub Pages project path, if any."
    )
    parsed = parser.parse_args(args)
    verify_static_site(parsed.root, parsed.base_path)
    print(f"PASS static site: {parsed.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
