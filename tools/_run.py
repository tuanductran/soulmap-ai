from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def python_executable(repo_root: Path) -> str:
    """
    Prefer the repository's local `.venv` Python when not already running inside a venv.

    This avoids confusing "missing dependency" errors when users run `python -m tools.*`
    without activating the virtual environment first.
    """

    # Track whether we've already printed a `.venv` notice, without using a module-level global.
    if not hasattr(python_executable, "_venv_notice_printed"):
        python_executable._venv_notice_printed = False  # type: ignore[attr-defined]

    if os.environ.get("VIRTUAL_ENV"):
        return sys.executable

    candidates = [
        repo_root / ".venv" / "bin" / "python",
        repo_root / ".venv" / "Scripts" / "python.exe",  # Windows
        repo_root / ".venv" / "Scripts" / "python",  # Windows (some envs)
    ]
    for candidate in candidates:
        if candidate.exists():
            if (
                not python_executable._venv_notice_printed  # type: ignore[attr-defined]
                and str(candidate) != sys.executable
            ):
                python_executable._venv_notice_printed = True  # type: ignore[attr-defined]
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

    if not python_executable._venv_notice_printed:  # type: ignore[attr-defined]
        python_executable._venv_notice_printed = True  # type: ignore[attr-defined]
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
