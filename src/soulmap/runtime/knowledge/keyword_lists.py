"""SoulMap compatibility boundary for Markdown keyword loading.

The parser primitives live in :mod:`soulmate.knowledge.markdown`. This module
keeps the established SoulMap imports stable and retains repository-specific
skill path resolution here.
"""

from __future__ import annotations

import os
from pathlib import Path

from soulmate.knowledge.markdown import (
    extract_keyword_section,
    extract_labeled_groups,
    load_keyword_section,
    load_labeled_groups,
)

__all__ = [
    "default_skill_path",
    "extract_keyword_section",
    "extract_labeled_groups",
    "load_keyword_section",
    "load_labeled_groups",
]


def default_skill_path(relative_path: str) -> Path:
    """Locate a file under ``skills/`` without depending on devtools.

    This resolver is SoulMap-specific because it knows the repository layout
    and the ``SOULMAP_REPO_ROOT`` environment variable. The generic parser
    functions are provided by Soulmate and accept explicit text or paths.
    """

    rel = Path(relative_path)
    env_root = os.environ.get("SOULMAP_REPO_ROOT")
    if env_root:
        candidate = Path(env_root) / rel
        if candidate.exists():
            return candidate

    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for parent in (base, *base.parents):
            candidate = parent / rel
            if candidate.exists():
                return candidate

    raise FileNotFoundError(
        f"Could not locate {relative_path}; set SOULMAP_REPO_ROOT or run from "
        "within the soulmap-ai repo."
    )
