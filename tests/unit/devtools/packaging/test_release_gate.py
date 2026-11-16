"""Tests for the consolidated release verification gate."""

import json
from pathlib import Path

import pytest

from soulmap.devtools.packaging import release_ops


def test_run_release_gate_preserves_verification_lifecycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    def verify_release(root: Path) -> dict[str, object]:
        calls.append("verify")
        return {"status": "pass", "version": "0.11.0"}

    def create_provenance(
        root: Path, verification: dict[str, object]
    ) -> dict[str, object]:
        calls.append("provenance")
        return {"status": "pass", "version": verification["version"]}

    def verify_provenance(root: Path, path: Path) -> dict[str, object]:
        calls.append("health")
        return {"status": "pass", "version": "0.11.0"}

    monkeypatch.setattr(release_ops, "verify_release", verify_release)
    monkeypatch.setattr(release_ops, "create_provenance", create_provenance)
    monkeypatch.setattr(release_ops, "verify_provenance", verify_provenance)

    verification_path = tmp_path / "dist" / "release-verification.json"
    provenance_path = tmp_path / "dist" / "release-provenance.json"

    payload = release_ops.run_release_gate(tmp_path, verification_path, provenance_path)

    assert calls == ["verify", "provenance", "verify", "health", "verify", "provenance"]
    assert payload["status"] == "pass"
    assert json.loads(verification_path.read_text())["version"] == "0.11.0"
    assert json.loads(provenance_path.read_text())["version"] == "0.11.0"
