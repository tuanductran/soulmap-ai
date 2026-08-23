"""Verify parity between the public web catalog and Library source catalog."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from soulmap.devtools.support.repo import REPO_ROOT

LIBRARY_CATALOG = Path("library/catalog.json")
PUBLIC_CATALOG = Path("web/content/catalog_data.json")
_INTERNAL_MARKERS = (
    "AGENTS.md",
    ".claude/",
    ".github/",
    "pyproject.toml",
    "uv.lock",
    "src/",
    "tests/",
)


@dataclass(frozen=True)
class PublicCatalogEntry:
    slug: str
    directory: str
    featured_file: str


def _read_public_catalog(repo_root: Path) -> tuple[PublicCatalogEntry, ...]:
    path = repo_root / PUBLIC_CATALOG
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing public catalog: {path}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        raise ValueError("public catalog entries must be a list")
    entries: list[PublicCatalogEntry] = []
    for raw_entry in payload["entries"]:
        if not isinstance(raw_entry, dict):
            raise ValueError("public catalog entries must be objects")
        slug = raw_entry.get("slug")
        directory = raw_entry.get("directory")
        featured_file = raw_entry.get("featured_file")
        if (
            not isinstance(slug, str)
            or not slug
            or not isinstance(directory, str)
            or not directory
            or not isinstance(featured_file, str)
            or not featured_file
        ):
            raise ValueError("public catalog entry fields must be non-empty strings")
        entries.append(PublicCatalogEntry(slug, directory, featured_file))
    return tuple(entries)


def _sanitize_public_markdown(markdown: str) -> str:
    for marker in _INTERNAL_MARKERS:
        markdown = markdown.replace(marker, "repository internals")
    return markdown


def _public_bundle(repo_root: Path, entry: PublicCatalogEntry) -> str:
    directory = repo_root / "skills" / entry.directory
    return "\n".join(
        _sanitize_public_markdown(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.md"))
    )


CATALOG = _read_public_catalog(REPO_ROOT)


def _read_library_catalog(repo_root: Path) -> dict[str, Any]:
    path = repo_root / LIBRARY_CATALOG
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing Library catalog: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Library catalog is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Library catalog must be a JSON object")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Library catalog entries must be a list")
    return payload


def _entry_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for raw_entry in payload["entries"]:
        if not isinstance(raw_entry, dict):
            raise ValueError("Library catalog entries must be objects")
        entry_id = raw_entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError("Library catalog entry id must be a non-empty string")
        if entry_id in result:
            raise ValueError(f"duplicate Library catalog entry id: {entry_id}")
        result[entry_id] = raw_entry
    return result


def verify_catalog_parity(repo_root: Path = REPO_ROOT) -> list[str]:
    """Return human-readable parity errors; an empty list means PASS."""
    payload = _read_library_catalog(repo_root)
    library_entries = _entry_map(payload)
    errors: list[str] = []
    catalog_slugs = {entry.slug for entry in CATALOG}
    library_slugs = set(library_entries)

    for slug in sorted(catalog_slugs - library_slugs):
        errors.append(f"missing Library entry for public catalog slug: {slug}")
    for slug in sorted(library_slugs - catalog_slugs):
        errors.append(f"Library entry has no public catalog slug: {slug}")

    for entry in CATALOG:
        library_entry = library_entries.get(entry.slug)
        if library_entry is None:
            continue
        expected_path = Path("skills") / entry.directory
        actual_path = library_entry.get("path")
        if actual_path != expected_path.as_posix():
            errors.append(
                f"{entry.slug}: Library path {actual_path!r} does not match "
                f"{expected_path.as_posix()!r}"
            )

        skill_dir = (repo_root / expected_path).resolve()
        root = repo_root.resolve()
        if root not in skill_dir.parents or not skill_dir.is_dir():
            errors.append(f"{entry.slug}: missing Skill directory: {expected_path}")
            continue

        featured_path = skill_dir / entry.featured_file
        if not featured_path.is_file():
            errors.append(f"{entry.slug}: missing featured file: {entry.featured_file}")
        markdown_files = sorted(skill_dir.glob("*.md"))
        if not markdown_files:
            errors.append(f"{entry.slug}: Skill directory contains no Markdown files")

        public_bundle = _public_bundle(repo_root, entry)
        for marker in _INTERNAL_MARKERS:
            if marker in public_bundle:
                errors.append(
                    f"{entry.slug}: raw public bundle leaks internal marker {marker}"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    if argv:
        raise SystemExit("soulmap catalog-parity does not accept arguments")
    errors = verify_catalog_parity()
    if errors:
        for error in errors:
            print(f"FAIL catalog parity: {error}", file=sys.stderr)
        return 1
    print(f"PASS catalog parity: {len(CATALOG)} public Skill entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
