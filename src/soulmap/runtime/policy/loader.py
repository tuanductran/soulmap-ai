"""Load SoulMap's declarative policy metadata for governance checks."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_POLICY_INDEX = REPO_ROOT / "policies" / "policy-index.json"


@dataclass(frozen=True)
class PolicyBundle:
    """Loaded policy files indexed by their policy index ids."""

    index: dict[str, Any]
    files: dict[str, dict[str, Any]]

    def require_policy_ids(self, policy_ids: set[str]) -> None:
        """Raise ValueError if required policy ids are not present in loaded files."""

        available = collect_policy_ids(self.files.values())
        missing = sorted(policy_ids - available)
        if missing:
            msg = "Missing required policy ids: " + ", ".join(missing)
            raise ValueError(msg)


def load_policy_bundle(index_path: Path = DEFAULT_POLICY_INDEX) -> PolicyBundle:
    """Load the policy index and every file it references.

    This loader is intentionally behavior-neutral. It supports governance checks,
    diagnostics, and future traceability work without replacing existing detectors,
    classifiers, guards, or runtime constants.
    """

    index = _read_json(index_path)
    files: dict[str, dict[str, Any]] = {}
    for entry in index.get("files", []):
        policy_path = REPO_ROOT / entry["path"]
        files[entry["id"]] = _read_json(policy_path)
    return PolicyBundle(index=index, files=files)


def collect_policy_ids(policy_documents: Any) -> set[str]:
    """Collect top-level and nested policy ids from loaded JSON-like documents."""

    found: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            policy_id = value.get("policy_id") or value.get("id")
            if isinstance(policy_id, str):
                found.add(policy_id)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            for child in value:
                visit(child)

    visit(policy_documents)
    return found


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        document = json.load(file)
    if not isinstance(document, dict):
        msg = f"Policy document must be a JSON object: {path}"
        raise TypeError(msg)
    return document
