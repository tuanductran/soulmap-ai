"""Load deterministic framework-to-template mappings from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

@dataclass(frozen=True, slots=True)
class TemplateRule:
    framework: str
    mode: str
    word_range: str
    question_rule: str
    source_file: str

def _norm(value: str) -> str:
    return re.sub(r"\\s+", " ", value.strip())

@lru_cache(maxsize=1)
def load_template_rules() -> tuple[TemplateRule, ...]:
    path = default_skill_path("skills/meta/framework-template-map.md")
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^\\| Framework \\| Mode \\| Word Range \\| Question Rule \\| Source File \\|\\s*$\\n(?P<body>.*?)(?=\\n## Detailed Structure)", text, re.MULTILINE | re.DOTALL)
    if match is None:
        raise ValueError("Framework-template core mapping table is missing.")
    rules = []
    for line in match.group("body").splitlines():
        if not line.strip().startswith("|") or "---" in line:
            continue
        cells = [_norm(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) == 5:
            rules.append(TemplateRule(*cells))
    required = {"Crisis", "Dependency", "Existential", "Mirror (Stage 1)", "Integration and Celebration"}
    if not required.issubset({rule.framework for rule in rules}):
        raise ValueError("Framework-template mapping is incomplete.")
    return tuple(rules)

def resolve_template(primary: str, mode: str, context: dict[str, object]) -> TemplateRule:
    if primary == "GRIEF":
        grief = context.get("grief", context)
        variant = grief.get("grief_type", "ambiguous") if isinstance(grief, dict) else "ambiguous"
        target = f"Grief ({variant})"
    elif primary == "DE_ESCALATION":
        target = "De-escalation (HIGH)" if mode == "SANCTUARY" else "De-escalation (MODERATE)"
    elif primary == "MIRROR" and context.get("stage") == 1:
        target = "Mirror (Stage 1)"
    elif primary == "MIRROR":
        target = "Mirror (emotional)"
    elif primary == "INTEGRATION_CELEBRATION":
        target = "Integration and Celebration"
    else:
        target = primary.replace("_", " ").title()
    for rule in load_template_rules():
        if rule.framework == target:
            return rule
    raise ValueError(f"No template mapping for framework {primary!r} in mode {mode!r}.")