"""Compatibility exports for the Python-owned runtime source registry.

The canonical registry lives in soulmap.runtime.source_registry. This module
remains as a stable import surface for existing runtime knowledge consumers.
"""

from soulmap.runtime.source_registry import (
    REGISTRY,
    _has_heading,
    _registry,
    _validate_registry,
    runtime_section,
    runtime_skill_path,
)

__all__ = [
    "REGISTRY",
    "_has_heading",
    "_registry",
    "_validate_registry",
    "runtime_section",
    "runtime_skill_path",
]
