"""Load human-authored runtime-only language reference data."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import cast

LocaleSignals = dict[str, tuple[str, ...]]


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


def _load_document(path: Path, *, expected_domain: str) -> tuple[str, LocaleSignals]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Language reference must be an object: {path}")

    locale = payload.get("locale")
    domain = payload.get("domain")
    signals = payload.get("signals")
    if not isinstance(locale, str) or not locale:
        raise ValueError(f"Language reference has no locale: {path}")
    if domain != expected_domain:
        raise ValueError(f"Expected domain {expected_domain!r}, got {domain!r}: {path}")
    if not isinstance(signals, dict):
        raise ValueError(f"Language reference has no signals object: {path}")

    parsed: LocaleSignals = {}
    for name, phrases in signals.items():
        if not isinstance(name, str) or not isinstance(phrases, list):
            raise ValueError(f"Invalid signal group in language reference: {path}")
        if not all(isinstance(phrase, str) and phrase.strip() for phrase in phrases):
            raise ValueError(f"Invalid phrase in language reference: {path}")
        parsed[name] = tuple(dict.fromkeys(phrase.lower() for phrase in phrases))

    return locale, parsed


def load_locale_signal_groups(filename: str, *, domain: str) -> LocaleSignals:
    """Load and merge a signal document from every locale directory.

    Locale files are deliberately runtime-only and human-authored. The loader discovers
    ``reference/languages/<locale>/<filename>`` files so adding a reviewed locale does
    not require editing a detector module.
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
        del locale
        for name, phrases in signals.items():
            existing = merged.get(name, ())
            merged[name] = tuple(dict.fromkeys((*existing, *phrases)))

    return cast(LocaleSignals, merged)
