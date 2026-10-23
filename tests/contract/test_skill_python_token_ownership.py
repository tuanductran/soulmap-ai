from __future__ import annotations

import re

from soulmap.runtime.knowledge import labels
from soulmap.runtime.source_registry import runtime_skill_path

_MIGRATED_LABEL_SECTIONS = (
    (
        "orchestration",
        ("Routing policy",),
        (
            "FRAMEWORK_NAMES",
            "MODE_NAMES",
            "SECONDARY_NAMES",
            "BLOCKED_FRAMEWORK_NAMES",
            "INTENSITY_NAMES",
            "INSTRUCTION_NAMES",
        ),
    ),
    ("scope-classification", ("Scope policy",), ("SCOPE_CATEGORY_NAMES",)),
    (
        "integration-celebration",
        ("Guidance",),
        ("CELEBRATION_GUIDANCE_NAMES",),
    ),
    ("dependency-detection", ("Guidance",), ("DEPENDENCY_GUIDANCE_NAMES",)),
    (
        "meaning-integration",
        ("Detection policy", "Guidance"),
        ("INSIGHT_CLASSIFICATION_NAMES", "INSIGHT_GUIDANCE_NAMES"),
    ),
)
_FORMAT_FIELDS = ("{strength}", "{insight_type}", "{guidance}")


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
    next_heading = re.search(rf"^#{{1,{level}}}\s+", text[body_start:], re.MULTILINE)
    body_end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:body_end]


def test_migrated_python_labels_stay_out_of_skill_sections() -> None:
    """Guard the reader-facing labels migrated in this refactor slice."""
    findings: list[str] = []
    for source_id, headings, mapping_names in _MIGRATED_LABEL_SECTIONS:
        path = runtime_skill_path(source_id)
        text = path.read_text(encoding="utf-8")
        labels_to_check = {
            value for name in mapping_names for value in getattr(labels, name).values()
        }
        for heading in headings:
            section = _registered_section(text, heading)
            for token in labels_to_check:
                if "_" in token or token.isupper():
                    if re.search(
                        rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
                        section,
                    ):
                        findings.append(f"{source_id}:{heading}: {token}")
                elif any(
                    cell.strip() == token
                    for line in section.splitlines()
                    if line.lstrip().startswith("|")
                    for cell in line.strip().strip("|").split("|")
                ):
                    findings.append(f"{source_id}:{heading}: {token}")

            if source_id == "meaning-integration":
                for field in _FORMAT_FIELDS:
                    if field in section:
                        findings.append(f"{source_id}:{heading}: {field}")

    assert not findings, (
        "Migrated Python labels/format fields appear in Skill content:\n"
        + "\n".join(sorted(set(findings)))
    )
