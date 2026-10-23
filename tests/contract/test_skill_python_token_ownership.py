from __future__ import annotations

import ast
import re

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge import labels
from soulmap.runtime.source_registry import _registry, runtime_skill_path

_TABLE_CELL_RE = re.compile(r"^\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)


def _registered_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^(?P<marks>#{{1,6}})\s+{re.escape(heading)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        return ""
    level = len(match.group("marks"))
    body_start = match.end()
    next_heading = re.search(
        rf"^#{{1,{level}}}\s+", text[body_start:], re.MULTILINE
    )
    body_end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:body_end]


def _python_owned_labels() -> set[str]:
    values: set[str] = set()
    for name, mapping in vars(labels).items():
        if name.endswith("_NAMES") and isinstance(mapping, dict):
            values.update(value for value in mapping.values() if isinstance(value, str))

    runtime_root = REPO_ROOT / "src/soulmap/runtime"
    for path in runtime_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            value = None
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                value = node.slice.value
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and node.args
                and isinstance(node.args[0], ast.Constant)
            ):
                value = node.args[0].value
            if isinstance(value, str) and (
                "_" in value or "-" in value or value.isupper()
            ):
                values.add(value)
    return values


def _format_placeholders() -> set[str]:
    runtime_root = REPO_ROOT / "src/soulmap/runtime"
    placeholders: set[str] = set()
    for path in runtime_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute) or node.func.attr != "format":
                continue
            placeholders.update(
                f"{{{keyword.arg}}}" for keyword in node.keywords if keyword.arg
            )
    return placeholders


def test_python_tokens_stay_out_of_skill_sections() -> None:
    """Python runtime labels stay in Python; Skills expose reader-facing content."""
    internal_labels = _python_owned_labels()
    key_like_tokens = {
        token
        for token in internal_labels
        if "_" in token or "-" in token or token.isupper()
    }
    placeholders = _format_placeholders()
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

            for line in section.splitlines():
                stripped = line.strip()
                for token in key_like_tokens:
                    if re.search(
                        rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])",
                        line,
                    ):
                        findings.append(
                            f"{path.relative_to(REPO_ROOT)}:{heading}: "
                            f"Python label {token!r}"
                        )
                if stripped.startswith("|"):
                    for cell in _TABLE_CELL_RE.findall(line):
                        cell = cell.strip()
                        if cell in internal_labels:
                            findings.append(
                                f"{path.relative_to(REPO_ROOT)}:{heading}: "
                                f"table label {cell!r}"
                            )
                for token in placeholders:
                    if token in line:
                        findings.append(
                            f"{path.relative_to(REPO_ROOT)}:{heading}: "
                            f"Python format field {token!r}"
                        )

    assert not findings, (
        "Python-owned labels/format fields appear in registered Skill sections:\n"
        + "\n".join(sorted(set(findings)))
    )
