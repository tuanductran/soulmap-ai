from pathlib import Path

from soulmap.cli import _command_table

REPO_ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = REPO_ROOT / "docs" / "operations" / "OPERATIONS.md"


def test_experimental_modules_are_not_public_cli_commands() -> None:
    commands = _command_table()

    assert "biometric" not in commands
    assert "biometric-ingest" not in commands
    assert "memory" not in commands
    assert "memory-ledger" not in commands


def test_experimental_modules_keep_consent_and_privacy_boundary() -> None:
    content = OPERATIONS.read_text(encoding="utf-8")

    for marker in (
        "should not be enabled",
        "silently in production",
        "explicit user consent",
        "health-data retention policy",
        "opt-in features",
        "product-level privacy review",
    ):
        assert marker in content
