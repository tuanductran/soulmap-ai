from __future__ import annotations

import re
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.source_registry import _registry, runtime_skill_path

_IDENTIFIER_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+|"
    r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+)(?![A-Za-z0-9_])"
)
_PLACEHOLDER_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


def _registered_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^(?P<marks>#{1,6})\s+{re.escape(heading)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        return ""
    level = len(match.group("marks"))
    body_start = match.end()
    next_heading = re.search(rf"^#{{1,{level}}}\s+", text[body_start:], re.MULTILINE)
    body_end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:body_end]


def _python_runtime_tokens() -> tuple[set[str], set[str]]:
    runtime_root = REPO_ROOT / "src/soulmap/runtime"
    identifiers: set[str] = set()
    placeholders: set[str] = set()
    for path in runtime_root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        identifiers.update(_IDENTIFIER_RE.findall(source))
        placeholders.update(_PLACEHOLDER_RE.findall(source))
    return identifiers, placeholders


def test_python_owned_identifiers_and_placeholders_do_not_leak_into_skill_sections() -> None:
    """Registered Skill sections use reader-facing labels, not Python-owned tokens."""
    identifiers, placeholders = _python_runtime_tokens()
    registry = _registry()
    findings: list[str] = []

    for source_id, entry in registry.items():
        path = runtime_skill_path(source_id)
        text = path.read_text(encoding="utf-8")
        headings = [heading for heading in entry[1:] if heading != "-"]
        for heading in headings:
            section = _registered_section(text, heading)
            if not section:
                continue
            for token in identifiers:
                if re.search(
                    rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
                    section,
                ):
                    line = text[: text.find(section)].count("\n") + 1
                    findings.append(f"{path.relative_to(REPO_ROOT)}:{line}: {heading}: {token}")
            for token in placeholders:
                if token in section:
                    line = text[: text.find(section)].count("\n") + 1
                    findings.append(f"{path.relative_to(REPO_ROOT)}:{line}: {heading}: {token}")

    assert not findings, (
        "Python-owned identifier/placeholder tokens appear in registered Skill sections:\n"
        + "\n".join(sorted(set(findings)))
    )
