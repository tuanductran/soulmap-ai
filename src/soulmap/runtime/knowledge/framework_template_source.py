"""Load deterministic framework output constraints from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_ROW_RE = re.compile(
    r"^\|\s*(?P<framework>[^|]+?)\s*\|\s*(?P<runtime_framework>[^|]+?)\s*\|\s*"
    r"(?P<runtime_variant>[^|]+?)\s*\|\s*(?P<mode>[^|]+?)\s*\|\s*"
    r"(?P<word_range>[^|]+?)\s*\|\s*(?P<question_rule>[^|]+?)\s*\|\s*"
    r"(?P<source_file>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class TemplateRule:
    """Output constraints for one framework/mode mapping."""

    framework: str
    runtime_framework: str
    runtime_variant: str
    mode: str
    word_range: str
    question_rule: str
    source_file: str


@lru_cache(maxsize=1)
def load_template_rules() -> tuple[TemplateRule, ...]:
    """Read and validate the core framework/template mapping table."""
    path = runtime_skill_path("framework-template-map")
    text = path.read_text(encoding="utf-8")
    rules = tuple(
        TemplateRule(
            framework=match.group("framework").strip(),
            runtime_framework=match.group("runtime_framework").strip(),
            runtime_variant=match.group("runtime_variant").strip(),
            mode=match.group("mode").strip(),
            word_range=match.group("word_range").strip(),
            question_rule=match.group("question_rule").strip(),
            source_file=match.group("source_file").strip(),
        )
        for match in _ROW_RE.finditer(text)
    )
    if not rules:
        raise ValueError("Framework template mapping table is missing.")
    keys = [(rule.runtime_framework, rule.runtime_variant) for rule in rules]
    if any(not framework or not variant for framework, variant in keys):
        raise ValueError("Framework template runtime identifiers are incomplete.")
    if len(keys) != len(set(keys)):
        raise ValueError("Framework template runtime identifiers must be unique.")
    return rules


def resolve_template(
    framework: str,
    mode: str,
    context: dict[str, object] | None = None,
) -> dict[str, str]:
    """Resolve the deterministic template contract for a routing selection."""
    context = context or {}
    runtime_framework = framework.strip().upper()
    variant = "default"
    if runtime_framework == "DE_ESCALATION":
        variant = "high" if mode == "SANCTUARY" else "moderate"
    elif runtime_framework == "GRIEF":
        grief_value = context.get("grief")
        grief_context = grief_value if isinstance(grief_value, dict) else context
        variant = str(
            grief_context.get("grief_type", grief_context.get("type", "acute"))
        ).lower()
    elif runtime_framework == "MIRROR":
        variant = "stage_1" if context.get("stage_override") else "emotional"

    for rule in load_template_rules():
        if (
            rule.runtime_framework == runtime_framework
            and rule.runtime_variant == variant
        ):
            return {
                "name": rule.framework,
                "mode": rule.mode,
                "word_range": rule.word_range,
                "question_rule": rule.question_rule,
                "source_file": rule.source_file,
            }
    raise ValueError(
        f"No framework template mapping exists for {framework!r} in mode {mode!r}."
    )
