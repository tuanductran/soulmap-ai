"""Load human-authored runtime language references from Markdown."""

from __future__ import annotations

import os
from pathlib import Path

from soulmap.runtime.knowledge.keyword_lists import extract_keyword_section

LocaleSignals = dict[str, tuple[str, ...]]

_SECTION_KEYS = {
    "Bypass: Dismissing Pain": "bypass_dismissing_pain",
    "Bypass: Premature Acceptance": "bypass_premature_acceptance",
    "Bypass: Spiritual Inflation": "bypass_spiritual_inflation",
    "Bypass: Bypassing Accountability": "bypass_accountability",
    "Genuine Integration Signals": "genuine_integration",
}


def _find_repo_file(relative_path: str) -> Path:
    relative = Path(relative_path)
    env_root = os.environ.get("SOULMAP_REPO_ROOT")
    if env_root:
        candidate = Path(env_root) / relative
        if candidate.exists():
            return candidate

    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for parent in (base, *base.parents):
            candidate = parent / relative
            if candidate.exists():
                return candidate

    raise FileNotFoundError(
        f"Could not locate {relative_path}; set SOULMAP_REPO_ROOT or run from "
        "within the soulmap-ai repo."
    )


def _parse_front_matter(text: str, path: Path) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Language reference has no front matter: {path}")

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"Invalid front matter in language reference: {path}")
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    raise ValueError(f"Language reference has unclosed front matter: {path}")


def _load_document(path: Path, *, expected_domain: str) -> tuple[str, LocaleSignals]:
    text = path.read_text(encoding="utf-8")
    metadata = _parse_front_matter(text, path)
    locale = metadata.get("locale", "")
    domain = metadata.get("domain")
    if not locale:
        raise ValueError(f"Language reference has no locale: {path}")
    if metadata.get("schema_version") != "1.0":
        raise ValueError(f"Language reference has unsupported schema: {path}")
    if domain != expected_domain:
        raise ValueError(f"Expected domain {expected_domain!r}, got {domain!r}: {path}")

    parsed: LocaleSignals = {}
    for heading, group in _SECTION_KEYS.items():
        phrases = extract_keyword_section(text, heading)
        if phrases:
            parsed[group] = phrases

    if not parsed:
        raise ValueError(f"Language reference has no signal sections: {path}")
    return locale, parsed


def load_locale_signal_groups(filename: str, *, domain: str) -> LocaleSignals:
    """Load and merge Markdown signal documents from every locale directory.

    Locale files are runtime-only and human-authored. The loader discovers
    ``reference/languages/<locale>/<filename>`` files so adding a reviewed locale
    does not require editing a detector module.
    """
    reference_root = _find_repo_file("reference/languages")
    merged: LocaleSignals = {}
    for path in sorted(reference_root.glob(f"*/{filename}")):
        locale, signals = _load_document(path, expected_domain=domain)
        directory_locale = path.parent.name
        if locale != directory_locale:
            raise ValueError(
                f"Locale {locale!r} does not match directory {directory_locale!r}: "
                f"{path}"
            )
        for name, phrases in signals.items():
            existing = merged.get(name, ())
            merged[name] = tuple(dict.fromkeys((*existing, *phrases)))

    return merged
