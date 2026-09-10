"""Bounded, opt-in session continuity with explicit memory boundaries."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from soulmap.runtime.io.cli_payload import parse_json_object, require_str_field

ALLOWED_MEMORY_KINDS = frozenset({"insight", "preference", "recurring_theme"})
DEFAULT_RETENTION = timedelta(days=30)


@dataclass(frozen=True)
class MemoryItem:
    """A user-confirmed, non-sensitive continuity item."""

    kind: str
    value: str
    confirmed_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        """Validate the immutable memory item's structural boundaries."""
        if self.kind not in ALLOWED_MEMORY_KINDS:
            raise ValueError(f"unsupported memory kind: {self.kind}")
        if not self.value.strip():
            raise ValueError("memory value must not be empty")
        if self.confirmed_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("memory timestamps must be timezone-aware")
        if self.expires_at <= self.confirmed_at:
            raise ValueError("memory expiry must be after confirmation")


class MemoryLedger:
    """In-process bounded ledger; persistence belongs to the host platform."""

    def __init__(self, entries: tuple[MemoryItem, ...] = ()) -> None:
        """Initialize the ledger with validated entries."""
        self._entries = tuple(entries)

    @property
    def entries(self) -> tuple[MemoryItem, ...]:
        """Return currently stored entries without mutating the ledger."""
        return self._entries

    def add(
        self,
        *,
        kind: str,
        value: str,
        user_confirmed: bool,
        sensitive: bool | None,
        identifying: bool = False,
        now: datetime | None = None,
        retention: timedelta = DEFAULT_RETENTION,
    ) -> MemoryItem:
        """Add an item only after explicit confirmation and boundary checks."""
        if not user_confirmed:
            raise ValueError("memory requires explicit user confirmation")
        if sensitive is not False:
            raise ValueError("memory sensitivity must be explicitly false")
        if identifying:
            raise ValueError("identifying content cannot be persisted")
        if retention <= timedelta(0):
            raise ValueError("retention must be positive")
        timestamp = now or datetime.now(UTC)
        if timestamp.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        item = MemoryItem(
            kind=kind,
            value=value,
            confirmed_at=timestamp,
            expires_at=timestamp + retention,
        )
        self._entries = (*self._entries, item)
        return item

    def read(self, *, now: datetime | None = None) -> tuple[MemoryItem, ...]:
        """Return only non-expired entries; stale entries are not surfaced."""
        timestamp = now or datetime.now(UTC)
        if timestamp.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        return tuple(item for item in self._entries if item.expires_at > timestamp)

    def prune(self, *, now: datetime | None = None) -> None:
        """Delete expired entries deterministically."""
        self._entries = self.read(now=now)

    def reset(self) -> None:
        """Delete all continuity state from this ledger."""
        self._entries = ()


def process_insight(
    user_response: str,
    last_insight: str,
    session_id: str,
    *,
    sensitive: bool | None = None,
    identifying: bool = False,
) -> dict[str, object]:
    """Process an explicit request to retain an insight.

    ``sensitive`` is intentionally required at the persistence boundary. A
    missing classification never becomes permission to store the text.
    ``session_id`` is a transient routing reference and is not persisted as
    memory content.
    """
    if user_response.lower() in ("no", "discard", "forget"):
        return {
            "status": "FORGOTTEN",
            "ledger_entry": None,
            "session_ref": session_id,
        }

    if sensitive is not False or identifying:
        return {
            "status": "NOT_ELIGIBLE",
            "ledger_entry": None,
            "session_ref": session_id,
        }

    ledger_content = f"Insight: {last_insight}\n"
    return {
        "status": "SAVED",
        "ledger_entry": ledger_content,
        "session_ref": session_id,
        "instruction": "Acknowledge their choice briefly and return to neutral. Never imply that retaining this insight creates a relationship obligation.",
    }


def main() -> int:
    """Process one ledger decision from a JSON payload on standard input."""
    data = parse_json_object(sys.stdin.read())
    user_response = require_str_field(data, "user_response")
    last_insight = require_str_field(data, "last_insight")
    session_id = require_str_field(data, "session_id") or "default_guest"
    sensitive_value = data.get("sensitive")
    sensitive = sensitive_value if isinstance(sensitive_value, bool) else None
    identifying_value = data.get("identifying", False)
    identifying = identifying_value if isinstance(identifying_value, bool) else True

    result = process_insight(
        user_response,
        last_insight,
        session_id,
        sensitive=sensitive,
        identifying=identifying,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        raise SystemExit(1) from error
