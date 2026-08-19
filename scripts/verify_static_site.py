from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_FILES = {
    "index.html",
    "how-it-works/index.html",
    "boundaries/index.html",
    "download/index.html",
    "notes/index.html",
    "about/index.html",
    "skills/index.html",
    "vi/index.html",
    "static/site.css",
    "static/site.js",
    "api/skills.json",
    "api/skills/meta/prompts.json",
    "api/skills/meta/prompts.vi.json",
    "api/raw/meta.md",
    "robots.txt",
}
FORBIDDEN_FILE_PARTS = {".claude", ".github", ".git", "dist", "src", "tests"}
FORBIDDEN_SUFFIXES = {".py", ".toml", ".lock"}


def _normalise_base_path(base_path: str) -> str:
    cleaned = base_path.strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def _is_allowed_generated_file(relative: Path) -> bool:
    if relative.as_posix().startswith("api/raw/") and relative.suffix == ".md":
        return True
    if relative.as_posix().startswith("partials/") and relative.suffix == ".html":
        return True
    return relative.as_posix() == "static/site.js"


def _validate_local_links(content: str, normalised_base: str, html_path: Path) -> None:
    links = re.findall(r'(?:href|src|hx-get)="([^"]+)"', content)
    local_links = [link for link in links if link.startswith("/")]
    if normalised_base:
        invalid_links = [
            link for link in local_links if not link.startswith(normalised_base + "/")
        ]
        if invalid_links:
            raise ValueError(
                f"{html_path} contains links outside base path: {invalid_links}"
            )


def _validate_script_tag(
    script_tag: str, normalised_base: str, html_path: Path
) -> None:
    source_match = re.search(r'\bsrc\s*=\s*"([^"]+)"', script_tag, re.IGNORECASE)
    if source_match is None:
        return
    script_src = source_match.group(1)
    if (
        script_src.startswith("/")
        and normalised_base
        and not script_src.startswith(normalised_base + "/")
    ):
        raise ValueError(f"{html_path} contains script outside base path: {script_src}")

    parsed_src = urlparse(script_src)
    if not (parsed_src.scheme or parsed_src.netloc):
        return
    if (
        parsed_src.scheme.lower() != "https"
        or parsed_src.hostname != "cdn.jsdelivr.net"
        or parsed_src.port is not None
        or parsed_src.username is not None
        or parsed_src.password is not None
    ):
        raise ValueError(
            f"{html_path} contains unapproved external script: {script_src}"
        )
    if not re.search(r'integrity="sha384-[^"]+"', script_tag, re.IGNORECASE):
        raise ValueError(f"{html_path} CDN script is missing SRI: {html_path}")


def verify_static_site(root: Path, base_path: str = "") -> None:
    """Raise ``ValueError`` when ``root`` is not a safe static site directory."""
    root = root.resolve()
    normalised_base = _normalise_base_path(base_path)
    if not root.is_dir():
        raise ValueError(f"static site directory does not exist: {root}")

    files = {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }
    missing = REQUIRED_FILES - files
    if missing:
        raise ValueError(f"missing static site files: {sorted(missing)}")

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
        if (
            path.is_file()
            and path.suffix in {".md", ".js"}
            and not _is_allowed_generated_file(relative)
        ):
            raise ValueError(
                f"static site contains unexpected generated source: {relative}"
            )

    for html_path in sorted(root.rglob("*.html")):
        if html_path.relative_to(root).as_posix().startswith("partials/"):
            continue
        content = html_path.read_text(encoding="utf-8")
        required_markers = ("<html lang=", 'name="viewport"', 'id="main-content"')
        missing_markers = [
            marker for marker in required_markers if marker not in content
        ]
        if missing_markers:
            raise ValueError(
                f"{html_path.relative_to(root)} missing markers: {missing_markers}"
            )
        if "127.0.0.1" in content or "localhost" in content:
            raise ValueError(
                f"{html_path.relative_to(root)} contains local development host"
            )
        _validate_local_links(content, normalised_base, html_path.relative_to(root))
        for script_tag in re.findall(r"<script\b[^>]*>", content, re.IGNORECASE):
            _validate_script_tag(
                script_tag, normalised_base, html_path.relative_to(root)
            )


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a generated SoulMap static site."
    )
    parser.add_argument("root", type=Path, help="static output directory")
    parser.add_argument(
        "--base-path", default="", help="expected GitHub Pages project path"
    )
    parsed = parser.parse_args(args)
    verify_static_site(parsed.root, parsed.base_path)
    print(f"PASS static site: {parsed.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
