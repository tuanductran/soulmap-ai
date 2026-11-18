from __future__ import annotations

import pytest

from soulmap.devtools.evals import eval_markdown_contracts


def test_markdown_contract_eval_fails_when_dataset_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(eval_markdown_contracts, "_load_cases", lambda: [])

    result = eval_markdown_contracts.run_markdown_contract_eval()

    assert result["ok"] is False
    assert result["summary"] == {"cases": 0, "rules": 0, "failed_checks": 1}
    assert result["results"] == []


def test_markdown_contract_eval_fails_when_case_filter_matches_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        eval_markdown_contracts,
        "_load_cases",
        lambda: [{"id": "known", "summary": "known case"}],
    )

    result = eval_markdown_contracts.run_markdown_contract_eval(
        case_id="misspelled"
    )

    assert result["ok"] is False
    assert result["summary"] == {"cases": 0, "rules": 0, "failed_checks": 1}
    assert result["results"] == []
