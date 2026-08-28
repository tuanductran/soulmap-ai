"""Create the local virtual environment and install the git hooks.

This is the implementation behind ``scripts/bootstrap_venv.sh``. It syncs the
locked dependency set with uv and, in a git checkout, installs the lefthook
commit hooks.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT

PYTHON_VERSION = "3.11"


def _venv_executable(venv_dir: Path, name: str) -> Path:
    """Return the path to an executable inside a virtual environment.

    Args:
        venv_dir: Root directory of the virtual environment.
        name: Base name of the executable, without any platform suffix.

    Returns:
        The platform-correct path, using ``Scripts`` and an ``.exe`` suffix on
        Windows and ``bin`` elsewhere.
    """
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _uv_executable() -> str:
    """Locate the uv executable on PATH.

    Returns:
        The absolute path to the uv executable.

    Raises:
        SystemExit: If uv is not installed, since bootstrap cannot continue
            without it.
    """
    uv_bin = shutil.which("uv")
    if uv_bin is None:
        raise SystemExit(
            "Error: `uv` is required for bootstrap. Install uv and rerun "
            "`bash scripts/bootstrap_venv.sh`."
        )
    return uv_bin


def _run(args: list[str], *, cwd: Path) -> None:
    """Run a subprocess and raise if it fails.

    Args:
        args: Full command line to execute.
        cwd: Working directory for the subprocess.

    Raises:
        subprocess.CalledProcessError: If the command exits non-zero.
    """
    subprocess.run(args, cwd=str(cwd), check=True)


def main(argv: list[str] | None = None) -> int:
    """Sync the virtual environment and install git hooks.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        The process exit code, 0 on success.
    """
    parser = argparse.ArgumentParser(
        description="Bootstrap the local .venv and install git hooks."
    )
    parser.parse_args(argv)
    repo_root = REPO_ROOT
    venv_dir = repo_root / ".venv"

    uv_bin = _uv_executable()
    _run(
        [
            uv_bin,
            "sync",
            "--locked",
            "--python",
            PYTHON_VERSION,
        ],
        cwd=repo_root,
    )
    if (repo_root / ".git").exists():
        _run([str(_venv_executable(venv_dir, "lefthook")), "install"], cwd=repo_root)
    else:
        print("info: skipping lefthook install because this is not a git checkout")

    if os.name == "nt":
        print("OK: venv ready. Activate with:")
        print(r"  .venv\Scripts\activate")
    else:
        print("OK: venv ready. Activate with:")
        print("  source .venv/bin/activate")
    if (repo_root / ".git").exists():
        print("Git hooks installed via lefthook")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
