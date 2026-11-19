from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "post-edit-evals.sh"


@pytest.mark.parametrize(
    ("dataset", "expected_command"),
    [
        ("groups.json", "run soulmap eval-groups"),
        ("markdown_contract_cases.json", "run soulmap eval-markdown-contracts"),
        ("response_generation_cases.json", "run soulmap eval-responses"),
        ("response_quality_cases.json", "run soulmap eval-response-quality"),
        (
            "safety_test_cases.json",
            "run python tests/eval_regression/test_safety_evals.py",
        ),
    ],
)
def test_post_edit_eval_hook_dispatches_each_dataset(
    tmp_path: Path, dataset: str, expected_command: str
) -> None:
    repo_root = tmp_path / "repo"
    dataset_path = repo_root / "evals" / "datasets" / dataset
    dataset_path.parent.mkdir(parents=True)
    dataset_path.write_text("[]\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    uv = fake_bin / "uv"
    uv.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$*" >> "$HOOK_CALL_LOG"\n',
        encoding="utf-8",
    )
    uv.chmod(0o755)

    call_log = tmp_path / "uv-calls.txt"
    env = os.environ.copy()
    env.update(
        {
            "CODEX_PROJECT_DIR": str(repo_root),
            "HOOK_CALL_LOG": str(call_log),
            "PATH": f"{fake_bin}{os.pathsep}{env.get('PATH', '')}",
        }
    )
    payload = {"tool_input": {"file_path": str(dataset_path)}}

    result = subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert call_log.read_text(encoding="utf-8").splitlines() == [expected_command]
