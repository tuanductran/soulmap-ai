"""Framework-neutral contracts for named knowledge resources."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ResourceContractError(ValueError):
    """Raised when a resource reference cannot satisfy the library contract."""


class ResourceLoader(Protocol):
    """Resolve and load an explicitly named resource."""

    def load(self, reference: ResourceReference) -> str:
        """Return the UTF-8 content for a validated resource reference."""
        ...


class ResourceReference:
    """A provider-neutral reference to one named knowledge resource."""

    def __init__(self, name: str, path: Path) -> None:
        if not name or not name.strip():
            raise ResourceContractError("Resource name must not be empty")
        if path.is_absolute():
            raise ResourceContractError("Resource path must be repository-relative")
        self.name = name
        self.path = path

    def __repr__(self) -> str:
        return f"ResourceReference(name={self.name!r}, path={self.path!s})"
