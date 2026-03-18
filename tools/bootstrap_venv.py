from __future__ import annotations

import os
from pathlib import Path
import subprocess
import venv

from tools._repo import REPO_ROOT


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _run(args: list[str], *, cwd: Path) -> None:
    subprocess.run(args, cwd=str(cwd), check=True)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    repo_root = REPO_ROOT
    venv_dir = repo_root / ".venv"

    if not venv_dir.exists():
        venv.EnvBuilder(with_pip=True).create(str(venv_dir))

    py = _venv_python(venv_dir)
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip"], cwd=repo_root)

    req_runtime = repo_root / "requirements.txt"
    req_dev = repo_root / "requirements-dev.txt"
    if req_runtime.is_file():
        _run([str(py), "-m", "pip", "install", "-r", str(req_runtime)], cwd=repo_root)
    if req_dev.is_file():
        _run([str(py), "-m", "pip", "install", "-r", str(req_dev)], cwd=repo_root)

    if os.name == "nt":
        print("OK: venv ready. Activate with:")
        print(r"  .venv\Scripts\activate")
    else:
        print("OK: venv ready. Activate with:")
        print("  source .venv/bin/activate")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
