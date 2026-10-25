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
    ("anger-companion", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("ancestral-patterns", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("dark-night-of-soul", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("empath-boundary", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("divine-guidance", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("soulmate-longing", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("soul-nourishment", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("sacred-feminine-masculine", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("spiritual-purpose", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("partnership-patterns", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("somatic-wellbeing", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("fear-of-visibility", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("creative-drought", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("grief-companion", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("inner-parts", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("perfectionism-paralysis", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("emotional-deescalation", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("pattern-mapper", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("life-direction", ("Detection policy", "Guidance"), ("RUNTIME_GUIDANCE_NAMES",)),
    ("spiritual-discernment", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("existential-companion", ("Detection policy", "Guidance"), ("RUNTIME_GUIDANCE_NAMES",)),
    ("shadow-patterns", ("Guidance",), ("RUNTIME_GUIDANCE_NAMES",)),
    ("conversation-synthesis", ("Detection policy", "Response guidance"), ("RUNTIME_GUIDANCE_NAMES",)),
    (
        "meaning-integration",
        ("Detection policy", "Guidance"),
        ("INSIGHT_CLASSIFICATION_NAMES", "INSIGHT_GUIDANCE_NAMES"),
    ),
)
_FORMAT_FIELDS_BY_SOURCE = {
    "meaning-integration": ("{strength}", "{insight_type}", "{guidance}"),
    "inner-parts": ("{primary_type}", "{parts}"),
    "grief-companion": ("{grief_type}", "{guidance}"),
    "existential-companion": ("{territory}", "{guidance}"),
    "conversation-synthesis": ("{theme}", "{count}", "{longitudinal_notice}", "{themes}"),
}


def _registered_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^(?P<marks>#{{1,6}})\s+{re.escape(heading)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"Expected Skill heading {heading!r} was not found.")
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
            prose = "\n".join(
                line for line in section.splitlines() if not line.lstrip().startswith("|")
            )
            table_keys = {
                line.strip().strip("|").split("|", 1)[0].strip()
                for line in section.splitlines()
                if line.lstrip().startswith("|")
            }
            for token in labels_to_check:
                if token in table_keys:
                    findings.append(f"{source_id}:{heading}: {token}")
                if ("_" in token or token.isupper()) and re.search(
                    rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
                    prose,
                ):
                    findings.append(f"{source_id}:{heading}: {token}")

            for field in _FORMAT_FIELDS_BY_SOURCE.get(source_id, ()):
                if field in section:
                    findings.append(f"{source_id}:{heading}: {field}")

    assert not findings, (
        "Migrated Python labels/format fields appear in Skill content:\n"
        + "\n".join(sorted(set(findings)))
    )
