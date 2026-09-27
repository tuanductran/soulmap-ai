"""Load scope classification keyword packs from Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from soulmap.runtime.knowledge.runtime_registry import runtime_skill_path

_CONTRACT_HEADING = "Runtime classification contract"


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


_PACK_RE = re.compile(r"^### (?P<pack>.+?)\s*$", re.MULTILINE)
_GROUP_RE = re.compile(r"^#### (?P<group>.+?)\s*$", re.MULTILINE)
_QUOTED_RE = re.compile(r'"([^"]+)"')


def _literal_config(body: str) -> dict[str, object]:
    packs = list(_PACK_RE.finditer(body))
    expected = {
        "Whitelist tier 1": "WHITELIST_TIER1",
        "Whitelist tier 2": "WHITELIST_TIER2",
        "Blacklist layer 1": "BLACKLIST_LAYER1",
        "Prohibited blacklist": "BLACKLIST_PROHIBITED",
    }
    if len(packs) != len(expected) or {match.group("pack") for match in packs} != set(
        expected
    ):
        raise ValueError("Scope runtime classification packs are incomplete.")
    values: dict[str, object] = {}
    for index, pack in enumerate(packs):
        end = packs[index + 1].start() if index + 1 < len(packs) else len(body)
        pack_body = body[pack.end() : end]
        groups = list(_GROUP_RE.finditer(pack_body))
        if not groups:
            raise ValueError(f"Scope pack {pack.group('pack')} has no categories.")
        parsed: dict[str, list[str]] = {}
        for group_index, group in enumerate(groups):
            group_end = (
                groups[group_index + 1].start()
                if group_index + 1 < len(groups)
                else len(pack_body)
            )
            phrases = _QUOTED_RE.findall(pack_body[group.end() : group_end])
            if not phrases:
                raise ValueError(f"Scope category {group.group('group')} is empty.")
            parsed[group.group("group")] = phrases
        values[expected[pack.group("pack")]] = parsed
    return values


def _freeze(value: dict[str, list[str]]) -> dict[str, tuple[str, ...]]:
    return {category: tuple(keywords) for category, keywords in value.items()}


@lru_cache(maxsize=1)
def load_scope_rules() -> ScopeRules:
    """Read and validate the runtime contract from shipped Markdown."""
    path = runtime_skill_path("scope-classification")
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
