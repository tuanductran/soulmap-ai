from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "src" / "soulmap" / "runtime"
KNOWLEDGE_ROOT = REPO_ROOT / "skills"
ACTIVATE_TARGET = re.compile(r"\bActivate ([A-Za-z0-9_-]+\.md)\b")


def _runtime_activate_targets() -> set[str]:
    targets: set[str] = set()
    for source_path in RUNTIME_ROOT.rglob("*.py"):
        targets.update(ACTIVATE_TARGET.findall(source_path.read_text(encoding="utf-8")))
    return targets


def test_runtime_activate_targets_exist_in_shipped_knowledge() -> None:
    targets = _runtime_activate_targets()
    shipped_knowledge = {
        knowledge_path.name for knowledge_path in KNOWLEDGE_ROOT.rglob("*.md")
    }

    assert targets
    assert not (targets - shipped_knowledge)
