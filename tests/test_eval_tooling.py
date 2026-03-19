"""Regression checks for eval tooling."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def test_eval_conversations_passes_default_suites() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.eval_conversations"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is True
