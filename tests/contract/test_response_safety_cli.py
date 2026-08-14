from __future__ import annotations

import io
import json

from soulmap.runtime.guards import response_safety_contract, response_safety_gate


def test_response_safety_contract_cli_serializes_a_pass_result(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        response_safety_contract.sys,
        "stdin",
        io.StringIO(json.dumps({"response_text": "What feels most present now?"})),
    )

    assert response_safety_contract.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "status": "PASS",
        "violations": [],
        "categories": [],
    }


def test_response_safety_gate_cli_preserves_safe_selection(monkeypatch, capsys) -> None:
    payload = {
        "message": "I keep noticing something I want to understand more clearly.",
        "history": [
            {
                "role": "user",
                "content": "I keep noticing something I want to understand more clearly.",
            }
        ],
        "memory": {},
        "selection": {"primary_framework": "MIRROR", "mode": "MIRROR"},
    }
    monkeypatch.setattr(
        response_safety_gate,
        "read_stdin_json",
        lambda: payload,
    )

    assert response_safety_gate.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "PASS"
    assert result["reason"] == "no_override"
    assert result["selection"] == payload["selection"]
