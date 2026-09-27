"""Load the executable orchestration contract from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

@dataclass(frozen=True, slots=True)
class OrchestrationRules:
    """Validated routing rules extracted from the orchestration skill."""
    priority: tuple[str, ...]
    secondary_layers: tuple[str, ...]
    modes: dict[str, str]
    valid_secondary: dict[str, tuple[str, ...]]
    forbidden_pairs: frozenset[frozenset[str]]
    stage1_stage: int
    stage1_max_user_turn: int
    stage1_framework: str
    stage1_depth: str
    breakthrough_framework: str

def _section(text: str, heading: str) -> str:
    marker = re.search(rf"^## {re.escape(heading)}\\s*$", text, re.MULTILINE)
    if marker is None:
        raise ValueError(f"Orchestration section {heading!r} is missing.")
    start = marker.end()
    next_heading = re.search(r"^## .+$", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]

def _rows(section: str, columns: int) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= columns and not all(set(cell) <= set(":- ") for cell in cells):
            rows.append(cells)
    return rows

def _framework(value: str) -> str:
    return re.sub(r"\\s+", " ", value.replace(" / Sanctuary", "").strip())

def _priority(text: str) -> tuple[str, ...]:
    section = _section(text, "Decision Tree")
    match = re.search(r"### Phase 3, primary framework selection(?P<body>.*?)(?=\\n### Phase 4,)", section, re.DOTALL)
    if match is None:
        raise ValueError("Primary framework priority table is missing.")
    values = tuple(_framework(row[1]) for row in _rows(match.group("body"), 3))
    if not {"Crisis", "Dependency", "Mirror", "Meaning Integration", "Synthesis", "Pattern"}.issubset(values):
        raise ValueError("Primary framework priority contract is incomplete.")
    return values

def _secondary(text: str) -> tuple[str, ...]:
    section = _section(text, "Decision Tree")
    match = re.search(r"### Phase 4, secondary layer selection(?P<body>.*?)(?=\\n### Phase 5,)", section, re.DOTALL)
    if match is None:
        raise ValueError("Secondary-layer contract is missing.")
    values = tuple(row[0].strip("`") for row in _rows(match.group("body"), 2))
    expected = {"anger", "bypass", "somatic", "meaning_integration", "inner_parts"}
    if set(values) != expected:
        raise ValueError("Secondary-layer contract is incomplete.")
    return values

def _modes(text: str) -> dict[str, str]:
    section = _section(text, "Response mode assignment")
    match = re.search(
        r"(?P<body>.*?)(?=\\n### Valid secondary combinations)",
        section,
        re.DOTALL,
    )
    if match is None:
        raise ValueError("Response mode table is missing.")
    values = {row[0]: row[2] for row in _rows(match.group("body"), 3)}
    if not {"Crisis", "Sanctuary", "Mirror", "PEER"}.issubset(values):
        raise ValueError("Response mode contract is incomplete.")
    return values

def _valid_secondary(text: str) -> dict[str, tuple[str, ...]]:
    section = _section(text, "Response mode assignment")
    match = re.search(r"### The following combinations are valid:(?P<body>.*?)(?=\\n### The following combinations are \\*\\*forbidden\\*\\*)", section, re.DOTALL)
    if match is None:
        raise ValueError("Valid secondary combination contract is missing.")
    result = {}
    for row in _rows(match.group("body"), 3):
        layers = tuple(part.strip().strip("`") for part in row[1].split(",") if part.strip().lower() != "none")
        result[_framework(row[0])] = layers
    return result

def _forbidden(text: str) -> frozenset[frozenset[str]]:
    section = _section(text, "Response mode assignment")
    match = re.search(r"### The following combinations are \\*\\*forbidden\\*\\*(?P<body>.*?)(?=\\n## Priority override rules)", section, re.DOTALL)
    if match is None:
        raise ValueError("Forbidden-combination contract is missing.")
    pairs = set()
    for line in match.group("body").splitlines():
        value = line.strip("- ")
        if " + " in value:
            left, right = (part.strip() for part in value.split(" + ", 1))
            pairs.add(frozenset({_framework(left), _framework(right)}))
    return frozenset(pairs)

def _overrides(text: str) -> tuple[int, int, str, str, str]:
    section = _section(text, "Priority override rules")
    stage = re.search(r"Rule 4, stage 1 overrides frameworks.*?Stage\\s+(\\d+).*?first or second.*?use\\s+([A-Za-z ]+?)\\s+with minimal depth", section, re.IGNORECASE | re.DOTALL)
    breakthrough = re.search(r"Rule 5, breakthrough overrides continuation.*?switch to\\s+([A-Za-z ]+?)\\s+immediately", section, re.IGNORECASE | re.DOTALL)
    if stage is None or breakthrough is None:
        raise ValueError("Stage-1 or breakthrough override contract is missing.")
    return int(stage.group(1)), 2, stage.group(2).strip().title(), "minimal", breakthrough.group(1).strip().title()

@lru_cache(maxsize=1)
def load_orchestration_rules() -> OrchestrationRules:
    """Read and validate the shipped orchestration Markdown contract."""
    path = default_skill_path("skills/meta/orchestration.md")
    text = path.read_text(encoding="utf-8")
    stage, max_turn, framework, depth, breakthrough = _overrides(text)
    return OrchestrationRules(
        priority=_priority(text),
        secondary_layers=_secondary(text),
        modes=_modes(text),
        valid_secondary=_valid_secondary(text),
        forbidden_pairs=_forbidden(text),
        stage1_stage=stage,
        stage1_max_user_turn=max_turn,
        stage1_framework=framework,
        stage1_depth=depth,
        breakthrough_framework=breakthrough,
    )