"""Resolve stable runtime knowledge identifiers through the shipped Markdown registry."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from soulmap.runtime.knowledge.keyword_lists import (
    default_skill_path,
    load_table_rows,
)

_REGISTRY_PATH = default_skill_path("skills/runtime/source-registry.md")


@lru_cache(maxsize=1)
def _registry() -> dict[str, tuple[str, str, str, str]]:
    rows = load_table_rows(_REGISTRY_PATH, "SoulMap runtime source registry")
    if not rows or any(len(row) != 5 for row in rows):
        raise ValueError("Runtime source registry must contain five columns.")

    result: dict[str, tuple[str, str, str, str]] = {}
    for source, path, signals, contract, guidance in rows:
        if source in result:
            raise ValueError(f"Duplicate runtime source: {source}")
        result[source] = (path, signals, contract, guidance)
    return result


def runtime_skill_path(source: str) -> Path:
    """Resolve one stable source identifier to its shipped Markdown file."""
    try:
        relative_path = _registry()[source][0]
    except KeyError as exc:
        raise KeyError(f"Unknown runtime knowledge source: {source}") from exc
    return default_skill_path(relative_path)


def runtime_section(source: str, kind: str) -> str:
    """Return the registered section heading for a runtime knowledge source."""
    fields = _registry().get(source)
    if fields is None:
        raise KeyError(f"Unknown runtime knowledge source: {source}")
    names = {
        "signals": fields[1],
        "contract": fields[2],
        "guidance": fields[3],
    }
    try:
        return names[kind]
    except KeyError as exc:
        raise KeyError(f"Unknown runtime knowledge section: {kind}") from exc
