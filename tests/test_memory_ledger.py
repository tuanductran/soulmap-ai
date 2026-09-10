from datetime import UTC, datetime, timedelta

import pytest

from soulmap.runtime.memory.memory_ledger import MemoryLedger, MemoryItem, process_insight


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def test_empty_memory_is_empty() -> None:
    assert MemoryLedger().read(now=NOW) == ()


def test_memory_requires_explicit_confirmation() -> None:
    ledger = MemoryLedger()
    with pytest.raises(ValueError, match="explicit user confirmation"):
        ledger.add(
            kind="insight",
            value="A useful observation",
            user_confirmed=False,
            sensitive=False,
            now=NOW,
        )


def test_sensitive_or_unclassified_memory_is_rejected() -> None:
    ledger = MemoryLedger()
    for sensitive in (True, None):
        with pytest.raises(ValueError, match="sensitivity"):
            ledger.add(
                kind="insight",
                value="Potentially sensitive content",
                user_confirmed=True,
                sensitive=sensitive,
                now=NOW,
            )


def test_identifying_memory_is_rejected() -> None:
    ledger = MemoryLedger()
    with pytest.raises(ValueError, match="identifying content"):
        ledger.add(
            kind="preference",
            value="Some value",
            user_confirmed=True,
            sensitive=False,
            identifying=True,
            now=NOW,
        )


def test_stale_memory_is_not_returned_and_can_be_pruned() -> None:
    ledger = MemoryLedger()
    ledger.add(
        kind="recurring_theme",
        value="A theme",
        user_confirmed=True,
        sensitive=False,
        now=NOW,
        retention=timedelta(days=1),
    )

    assert ledger.read(now=NOW + timedelta(days=1)) == ()
    ledger.prune(now=NOW + timedelta(days=1))
    assert ledger.entries == ()


def test_reset_removes_all_continuity_state() -> None:
    ledger = MemoryLedger()
    ledger.add(
        kind="preference",
        value="A preference",
        user_confirmed=True,
        sensitive=False,
        now=NOW,
    )
    ledger.reset()
    assert ledger.entries == ()


def test_malformed_memory_item_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported memory kind"):
        MemoryItem(
            kind="unknown",
            value="value",
            confirmed_at=NOW,
            expires_at=NOW + timedelta(days=1),
        )


def test_process_insight_never_defaults_to_persistence() -> None:
    result = process_insight("yes", "Keep this", "session-1")
    assert result["status"] == "NOT_ELIGIBLE"
    assert result["ledger_entry"] is None


def test_process_insight_requires_explicit_non_sensitive_classification() -> None:
    result = process_insight(
        "yes",
        "Keep this",
        "session-1",
        sensitive=False,
    )
    assert result["status"] == "SAVED"
    assert result["ledger_entry"] == "Insight: Keep this\n"


def test_declining_an_insight_forgets_it() -> None:
    result = process_insight("no", "Do not keep this", "session-1", sensitive=False)
    assert result == {
        "status": "FORGOTTEN",
        "ledger_entry": None,
        "session_ref": "session-1",
    }
