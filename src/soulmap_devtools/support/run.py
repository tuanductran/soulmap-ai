from __future__ import annotations

import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

if os.name == "nt":
    import msvcrt
else:
    import fcntl


def python_executable(repo_root: Path) -> str:
    """
    Prefer the repository's local `.venv` Python when not already running inside a venv.

    This avoids confusing "missing dependency" errors when users run the repo's Python
    tooling without activating the virtual environment first.
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


@contextmanager
def repo_tooling_lock(
    repo_root: Path,
    *,
    name: str = "format-lint",
    poll_interval_s: float = 0.1,
) -> Any:
    """Serialize repo-wide tooling that mutates or checks the same files."""
    # Prefer putting the lock file in the .venv to avoid cluttering the root.
    # The .venv is usually gitignored and hidden from casual view.
    venv_dir = repo_root / ".venv"
    if venv_dir.is_dir():
        lock_path = venv_dir / f".{name}.lock"
    else:
        lock_path = repo_root / f".{name}.lock"

    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+", encoding="utf-8") as lock_file:
        start = time.monotonic()
        notified = False

        while True:
            try:
                if os.name == "nt":
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if not notified and time.monotonic() - start >= 0.5:
                    notified = True
                    print(
                        f"info: waiting for repo tooling lock {lock_path.name}",
                        file=sys.stderr,
                    )
                time.sleep(poll_interval_s)

        try:
            yield
        finally:
            if os.name == "nt":
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    try:
        lock_path.unlink()
    except FileNotFoundError:
        return
    except OSError as exc:
        print(
            f"warning: failed to remove repo tooling lock {lock_path.name}: {exc}",
            file=sys.stderr,
        )
