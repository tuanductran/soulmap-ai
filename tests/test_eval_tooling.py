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


def test_eval_responses_passes_default_suite() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.eval_responses"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is True


def test_eval_groups_passes_default_suite() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.eval_groups"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["summary"]["asserted_items"] > 0
    assert data["summary"]["source_checks"] > 0
    assert data["summary"]["failed_source_checks"] == 0
    assert data["summary"]["source_marker_checks"] > 0
