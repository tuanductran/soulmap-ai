from __future__ import annotations

from soulmap_devtools.evals.eval_markdown_contracts import run_markdown_contract_eval


def test_markdown_contract_cases_pass() -> None:
    result = run_markdown_contract_eval()
    summary = result["summary"]
    assert isinstance(summary, dict)
    cases = summary.get("cases")
    assert isinstance(cases, int)
    assert cases > 0
    assert result["ok"], result
