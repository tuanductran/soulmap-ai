from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT

PYTHON_VERSION = "3.11"


def _venv_executable(venv_dir: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _uv_executable() -> str:
    uv_bin = shutil.which("uv")
    if uv_bin is None:
        raise SystemExit(
            "Error: `uv` is required for bootstrap. Install uv and rerun "
            "`bash scripts/bootstrap_venv.sh`."
        )
    return uv_bin


def _run(args: list[str], *, cwd: Path) -> None:
    subprocess.run(args, cwd=str(cwd), check=True)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    repo_root = REPO_ROOT
    venv_dir = repo_root / ".venv"

    uv_bin = _uv_executable()
    _run(
        [
            uv_bin,
            "sync",
            "--locked",
            "--extra",
            "dev",
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
