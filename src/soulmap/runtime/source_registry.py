"""Canonical runtime-to-knowledge source registry.

This module owns only runtime routing metadata. Domain meaning remains in the
shipped Markdown files under skills/; this registry does not copy their content.
"""

import re
from functools import cache
from pathlib import Path

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

REGISTRY: dict[str, tuple[str, str, str, str]] = {
    "anger-companion": (
        "skills/frameworks/anger-companion.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "ancestral-patterns": (
        "skills/frameworks/ancestral-patterns.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "conversation-synthesis": (
        "skills/frameworks/conversation-synthesis.md",
        "Detection signals",
        "Detection policy",
        "-",
    ),
    "creative-drought": (
        "skills/frameworks/creative-drought.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "dark-night-of-soul": (
        "skills/frameworks/dark-night-of-soul.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "divine-guidance": (
        "skills/frameworks/divine-guidance.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "emotional-deescalation": (
        "skills/frameworks/emotional-deescalation.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "empath-boundary": (
        "skills/frameworks/empath-boundary.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "existential-companion": (
        "skills/frameworks/existential-companion.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "fear-of-visibility": (
        "skills/frameworks/fear-of-visibility.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "framework-template-map": (
        "skills/meta/framework-template-map.md",
        "-",
        "-",
        "-",
    ),
    "orchestration": (
        "skills/meta/orchestration.md",
        "-",
        "Routing policy",
        "-",
    ),
    "scope-classification": (
        "skills/safety/whitelist-blacklist-system.md",
        "-",
        "Scope policy",
        "-",
    ),
    "stage-classifier": (
        "skills/meta/stage-classifier.md",
        "-",
        "Stage classification policy",
        "-",
    ),
    "grief-companion": (
        "skills/frameworks/grief-companion.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "inner-parts": (
        "skills/frameworks/inner-parts.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "integration-celebration": (
        "skills/frameworks/integration-celebration.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "meaning-integration": (
        "skills/frameworks/meaning-integration.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "perfectionism-paralysis": (
        "skills/frameworks/perfectionism-paralysis.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "partnership-patterns": (
        "skills/soulmate/partnership-patterns.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "sacred-feminine-masculine": (
        "skills/frameworks/sacred-feminine-masculine.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "shadow-patterns": (
        "skills/frameworks/shadow-patterns.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "self-compassion": (
        "skills/frameworks/self-compassion.md",
        "Detection signals",
        "-",
        "-",
    ),
    "somatic-wellbeing": (
        "skills/frameworks/somatic-wellbeing.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
    "soulmate-longing": (
        "skills/soulmate/soulmate-longing.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "soul-nourishment": (
        "skills/frameworks/soul-nourishment.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "spiritual-discernment": (
        "skills/spiritual/spiritual-discernment.md",
        "Detection signal reference",
        "Detection policy",
        "Guidance",
    ),
    "spiritual-purpose": (
        "skills/frameworks/spiritual-purpose.md",
        "Activation Signals",
        "Detection policy",
        "Guidance",
    ),
    "life-direction": (
        "skills/frameworks/life-direction.md",
        "Detection signals",
        "Detection policy",
        "Runtime guidance",
    ),
    "pattern-mapper": (
        "skills/frameworks/pattern-mapper.md",
        "Pattern 1",
        "Detection policy",
        "Runtime guidance",
    ),
    "dependency-detection": (
        "skills/safety/dependency-detection.md",
        "Detection signals",
        "Detection policy",
        "Guidance",
    ),
}


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
    repo_root: Path | None = None,
) -> tuple[str, ...]:
    """Validate every registry mapping against its shipped Markdown source."""
    violations: list[str] = []
    root = (repo_root or default_skill_path("skills").parent).resolve()
    skills_root = (root / "skills").resolve()

    for source, (relative_path, signals, contract, guidance) in entries.items():
        path = (root / relative_path).resolve()
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


@cache
def _registry(
    repo_root: Path | None = None,
) -> dict[str, tuple[str, str, str, str]]:
    """Return the Python-owned registry after validating shipped sources."""
    if repo_root is not None:
        return _registry_for_root(repo_root)
    violations = _validate_registry(REGISTRY)
    if violations:
        raise ValueError(
            "Runtime source registry validation failed:\n"
            + "\n".join(f"- {violation}" for violation in violations)
        )
    return REGISTRY


@cache
def _registry_for_root(repo_root: Path) -> dict[str, tuple[str, str, str, str]]:
    """Validate the registry against an explicitly supplied repository root."""
    violations = _validate_registry(REGISTRY, repo_root)
    if violations:
        raise ValueError(
            "Runtime source registry validation failed:\n"
            + "\n".join(f"- {violation}" for violation in violations)
        )
    return REGISTRY


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
