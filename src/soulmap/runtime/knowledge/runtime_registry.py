"""Resolve stable runtime knowledge identifiers through the repository Markdown registry."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from soulmap.runtime.knowledge.keyword_lists import default_skill_path, load_table_rows

_REGISTRY_PATH = default_skill_path("skills/runtime/source-registry.md")


@lru_cache(maxsize=None)
def _registry(registry_path: Path = _REGISTRY_PATH) -> dict[str, tuple[str, str, str, str]]:
    rows = load_table_rows(registry_path, "SoulMap runtime source registry")
    if not rows or any(len(row) != 5 for row in rows):
        raise ValueError("Runtime source registry must contain five columns.")

    result: dict[str, tuple[str, str, str, str]] = {}
    for source, path, signals, contract, guidance in rows:
        if source in result:
            raise ValueError(f"Duplicate runtime source: {source}")
        result[source] = (path, signals, contract, guidance)

    violations = _validate_registry(result)
    if violations:
        raise ValueError(
            "Runtime source registry validation failed:\n"
            + "\n".join(f"- {violation}" for violation in violations)
        )
    return result


def _has_heading(text: str, expected: str) -> bool:
    """Return whether Markdown contains the registered section heading."""
    if expected.startswith("Pattern "):
        return bool(
            re.search(
                rf"^##\s+{re.escape(expected)}:\s+.+$",
                text,
                re.MULTILINE,
            )
        )
    return bool(
        re.search(
            rf"^#{{2,3}}\s+{re.escape(expected)}\s*$",
            text,
            re.MULTILINE,
        )
    )


def _validate_registry(
    entries: dict[str, tuple[str, str, str, str]],
) -> tuple[str, ...]:
    """Validate every registry mapping and its required Markdown sections."""
    violations: list[str] = []
    skills_root = registry_path.parent.parent.resolve()

    for source, (relative_path, signals, contract, guidance) in entries.items():
        path = (registry_path.parent.parent / relative_path.removeprefix("skills/")).resolve()
        try:
            path.relative_to(skills_root)
        except ValueError:
            violations.append(f"{source}: path escapes skills/: {relative_path}")
            continue

        if not path.is_file():
            violations.append(f"{source}: source file does not exist: {relative_path}")
            continue

        text = path.read_text(encoding="utf-8")
        for kind, section in (
            ("signals", signals),
            ("contract", contract),
            ("guidance", guidance),
        ):
            if section != "-" and (not section or not _has_heading(text, section)):
                violations.append(
                    f"{source}: missing {kind} section {section!r} in {relative_path}"
                )

    return tuple(violations)


def runtime_skill_path(source: str) -> Path:
    """Resolve one stable source identifier to its repository Markdown file."""
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
