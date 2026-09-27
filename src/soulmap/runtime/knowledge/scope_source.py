"""Load scope classification keyword packs from Markdown."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from soulmap.runtime.knowledge.keyword_lists import default_skill_path

_CONTRACT_HEADING = "Runtime classification contract"
_BLOCK_RE = re.compile(
    r"\x60\x60\x60json\s*(?P<body>.*?)\x60\x60\x60",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class ScopeRules:
    """Executable scope keyword packs authored in whitelist-blacklist-system.md."""

    whitelist_tier1: dict[str, tuple[str, ...]]
    whitelist_tier2: dict[str, tuple[str, ...]]
    blacklist_layer1: dict[str, tuple[str, ...]]
    blacklist_prohibited: dict[str, tuple[str, ...]]


def _contract_body(text: str) -> str:
    match = re.search(
        rf"^## {re.escape(_CONTRACT_HEADING)}\s*$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("Scope runtime classification contract is missing.")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _literal_config(body: str) -> dict[str, object]:
    match = _BLOCK_RE.search(body)
    if match is None:
        raise ValueError("Scope runtime classification block is missing.")
    try:
        values = json.loads(match.group("body"))
    except json.JSONDecodeError as exc:
        raise ValueError("Scope runtime classification is invalid JSON.") from exc
    if not isinstance(values, dict):
        raise ValueError("Scope runtime classification must be an object.")
    required = {
        "WHITELIST_TIER1",
        "WHITELIST_TIER2",
        "BLACKLIST_LAYER1",
        "BLACKLIST_PROHIBITED",
    }
    if set(values) != required:
        raise ValueError("Scope runtime classification packs are incomplete.")
    for name in required:
        value = values[name]
        if not isinstance(value, dict) or not all(
            isinstance(category, str)
            and isinstance(keywords, list)
            and all(isinstance(keyword, str) and keyword for keyword in keywords)
            for category, keywords in value.items()
        ):
            raise ValueError(f"Scope keyword pack {name} is invalid.")
    return values

def _freeze(value: dict[str, list[str]]) -> dict[str, tuple[str, ...]]:
    return {category: tuple(keywords) for category, keywords in value.items()}


@lru_cache(maxsize=1)
def load_scope_rules() -> ScopeRules:
    """Read and validate the runtime contract from shipped Markdown."""
    path = default_skill_path("skills/safety/whitelist-blacklist-system.md")
    body = _contract_body(path.read_text(encoding="utf-8"))
    values = _literal_config(body)
    return ScopeRules(
        whitelist_tier1=_freeze(cast(dict[str, list[str]], values["WHITELIST_TIER1"])),
        whitelist_tier2=_freeze(cast(dict[str, list[str]], values["WHITELIST_TIER2"])),
        blacklist_layer1=_freeze(
            cast(dict[str, list[str]], values["BLACKLIST_LAYER1"])
        ),
        blacklist_prohibited=_freeze(
            cast(dict[str, list[str]], values["BLACKLIST_PROHIBITED"])
        ),
    )
