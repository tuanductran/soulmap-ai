from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Any, cast


def python_executable(repo_root: Path) -> str:
    """
    Prefer the repository's local `.venv` Python when not already running inside a venv.

    This avoids confusing "missing dependency" errors when users run `python -m tools.*`
    without activating the virtual environment first.
    """
    # Store "printed already" state on the function object, but keep type checkers happy.
    func_any = cast(Any, python_executable)
    notice_printed = bool(getattr(func_any, "_venv_notice_printed", False))
    if os.environ.get("VIRTUAL_ENV"):
        return sys.executable

    candidates = [
        repo_root / ".venv" / "bin" / "python",
        repo_root / ".venv" / "Scripts" / "python.exe",  # Windows
        repo_root / ".venv" / "Scripts" / "python",  # Windows (some envs)
    ]
    for candidate in candidates:
        if candidate.exists():
            if not notice_printed and str(candidate) != sys.executable:
                func_any._venv_notice_printed = True
                print(
                    f"info: detected local .venv, using {candidate}. "
                    "Activate it to match: "
                    "`source .venv/bin/activate` (macOS/Linux) or "
                    "`.venv\\\\Scripts\\\\activate` (Windows).",
                    file=sys.stderr,
                )
            return str(candidate)

    # Avoid noisy warnings in CI where a local `.venv` is typically not used.
    if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true":
        return sys.executable

    if not notice_printed:
        func_any._venv_notice_printed = True
        print(
            "warning: no local `.venv` detected and no active virtual environment. "
            "If you hit missing-tool errors, run `bash scripts/bootstrap_venv.sh` "
            "then activate `.venv`.",
            file=sys.stderr,
        )
    return sys.executable


def run(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        args,
        cwd=str(cwd),
        env=merged_env,
        text=True,
        check=check,
    )


def python_module(module: str, *extra_args: str, cwd: Path, check: bool = True) -> None:
    python = python_executable(cwd)
    run([python, "-m", module, *extra_args], cwd=cwd, check=check)
