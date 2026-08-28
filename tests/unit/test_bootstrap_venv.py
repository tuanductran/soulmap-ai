from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from soulmap.devtools.cli import bootstrap_venv


def test_venv_executable_covers_posix_and_windows_layouts(
    tmp_path: Path, monkeypatch
) -> None:
    venv_dir = tmp_path / ".venv"

    monkeypatch.setattr(bootstrap_venv, "os", SimpleNamespace(name="posix"))
    assert bootstrap_venv._venv_executable(venv_dir, "python") == (
        venv_dir / "bin" / "python"
    )

    monkeypatch.setattr(bootstrap_venv, "os", SimpleNamespace(name="nt"))
    assert bootstrap_venv._venv_executable(venv_dir, "python") == (
        venv_dir / "Scripts" / "python.exe"
    )


def test_uv_executable_and_run_wrapper_handle_success_and_missing_uv(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []
    monkeypatch.setattr(bootstrap_venv.shutil, "which", lambda _name: "/usr/bin/uv")
    assert bootstrap_venv._uv_executable() == "/usr/bin/uv"

    monkeypatch.setattr(
        bootstrap_venv.subprocess,
        "run",
        lambda args, **kwargs: calls.append((args, kwargs)),
    )
    bootstrap_venv._run(["uv", "sync"], cwd=tmp_path)
    assert calls == [(["uv", "sync"], {"cwd": str(tmp_path), "check": True})]

    monkeypatch.setattr(bootstrap_venv.shutil, "which", lambda _name: None)
    with pytest.raises(SystemExit, match="`uv` is required"):
        bootstrap_venv._uv_executable()


def test_bootstrap_main_reports_windows_activation_and_git_hooks(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    (tmp_path / ".git").mkdir()
    calls: list[list[str]] = []
    monkeypatch.setattr(bootstrap_venv, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(bootstrap_venv, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(bootstrap_venv, "_uv_executable", lambda: "uv")
    monkeypatch.setattr(
        bootstrap_venv,
        "_venv_executable",
        lambda _venv_dir, name: Path(f"C:/venv/{name}.exe"),
    )
    monkeypatch.setattr(
        bootstrap_venv,
        "_run",
        lambda args, *, cwd: calls.append(args),
    )

    assert bootstrap_venv.main([]) == 0

    assert calls[0] == [
        "uv",
        "sync",
        "--locked",
        "--python",
        bootstrap_venv.PYTHON_VERSION,
    ]
    assert calls[1][0].replace("\\", "/") == "C:/venv/lefthook.exe"
    assert calls[1][1] == "install"
    output = capsys.readouterr().out
    assert ".venv\\Scripts\\activate" in output
    assert "Git hooks installed via lefthook" in output
