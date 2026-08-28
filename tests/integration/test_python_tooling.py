from __future__ import annotations

import importlib
import runpy
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from soulmap import cli as soulmap_cli
from soulmap.devtools.cli import bootstrap_venv
from soulmap.devtools.quality import format as format_tool
from soulmap.devtools.quality import lint as lint_tool
from soulmap.devtools.support import repo as repo_support
from soulmap.devtools.support.repo import (
    python_source_paths,
    tracked_hygiene_violations,
)


@contextmanager
def _noop_lock(_repo_root: Path) -> Iterator[None]:
    yield


def test_python_source_paths_follow_repo_order(tmp_path: Path) -> None:
    for name in ["src", "tests", "scripts"]:
        (tmp_path / name).mkdir()
    (tmp_path / "docs").mkdir()

    assert python_source_paths(tmp_path) == [
        tmp_path / "src",
        tmp_path / "tests",
        tmp_path / "scripts",
    ]


def test_resolve_repo_root_prefers_cwd_checkout_when_package_path_is_elsewhere(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "pyproject.toml").write_text(
        "[project]\nname='demo'\n", encoding="utf-8"
    )
    (repo_root / "AGENTS.md").write_text("demo\n", encoding="utf-8")
    (repo_root / "src").mkdir()
    fake_module = (
        tmp_path
        / "venv"
        / "lib"
        / "python3.11"
        / "site-packages"
        / "soulmap"
        / "devtools"
        / "support"
        / "repo.py"
    )
    fake_module.parent.mkdir(parents=True)
    fake_module.write_text("# installed copy\n", encoding="utf-8")

    monkeypatch.delenv("SOULMAP_REPO_ROOT", raising=False)
    monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)
    monkeypatch.delenv("CODEX_PROJECT_DIR", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(repo_root)
    monkeypatch.setattr(repo_support, "__file__", str(fake_module))

    assert repo_support.resolve_repo_root() == repo_root


def test_format_relies_on_ruff_for_python_rewrites(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ["src", "tests", "scripts"]:
        (tmp_path / name).mkdir()

    calls: list[tuple[str, tuple[str, ...]]] = []

    monkeypatch.setattr(format_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(format_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(format_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(format_tool, "iter_markdown_files", lambda _root: [])

    def fake_python_module(
        module: str, *extra_args: str, cwd: Path, check: bool = True
    ) -> None:
        _ = cwd, check
        calls.append((module, extra_args))

    monkeypatch.setattr(format_tool, "python_module", fake_python_module)

    format_tool.main([])

    assert (
        "ruff",
        (
            "check",
            "--fix",
            str(tmp_path / "src"),
            str(tmp_path / "tests"),
            str(tmp_path / "scripts"),
        ),
    ) in calls
    assert (
        "ruff",
        (
            "format",
            str(tmp_path / "src"),
            str(tmp_path / "tests"),
            str(tmp_path / "scripts"),
        ),
    ) in calls
    assert not any(module == "isort" for module, _args in calls)


def test_format_runs_markdown_fix_for_existing_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "src").mkdir()
    markdown_file = tmp_path / "docs" / "guide.md"
    markdown_file.parent.mkdir()
    markdown_file.write_text("# Guide\n", encoding="utf-8")
    module_calls: list[tuple[str, tuple[str, ...]]] = []
    run_calls: list[tuple[list[str], bool]] = []

    monkeypatch.setattr(format_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(format_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(format_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(
        format_tool, "iter_markdown_files", lambda _root: [markdown_file]
    )

    def fake_python_module(
        module: str, *extra_args: str, cwd: Path, check: bool = True
    ) -> None:
        _ = cwd, check
        module_calls.append((module, extra_args))

    def fake_run(args: list[str], *, cwd: Path, check: bool) -> SimpleNamespace:
        _ = cwd
        run_calls.append((args, check))
        return SimpleNamespace(returncode=0, args=args)

    monkeypatch.setattr(format_tool, "python_module", fake_python_module)
    monkeypatch.setattr(format_tool, "run", fake_run)

    assert format_tool.main([]) == 0

    assert module_calls == [
        (
            "ruff",
            ("check", "--fix", str(tmp_path / "src")),
        ),
        ("ruff", ("format", str(tmp_path / "src"))),
    ]
    assert run_calls == [
        (
            [
                "python",
                "-m",
                "pymarkdown",
                "--config",
                ".pymarkdown.json",
                "fix",
                str(Path("docs") / "guide.md"),
            ],
            False,
        )
    ]


@pytest.mark.parametrize("returncode", [0, 3])
def test_format_accepts_pymarkdown_fix_statuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, returncode: int
) -> None:
    (tmp_path / "src").mkdir()
    markdown_file = tmp_path / "README.md"
    markdown_file.write_text("# README\n", encoding="utf-8")

    monkeypatch.setattr(format_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(format_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(format_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(
        format_tool, "iter_markdown_files", lambda _root: [markdown_file]
    )
    monkeypatch.setattr(format_tool, "python_module", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        format_tool,
        "run",
        lambda args, *, cwd, check: SimpleNamespace(returncode=returncode, args=args),
    )

    assert format_tool.main([]) == 0


def test_format_propagates_unexpected_pymarkdown_fix_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "src").mkdir()
    markdown_file = tmp_path / "README.md"
    markdown_file.write_text("# README\n", encoding="utf-8")
    command = ["python", "-m", "pymarkdown", "fix", "README.md"]

    monkeypatch.setattr(format_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(format_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(format_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(
        format_tool, "iter_markdown_files", lambda _root: [markdown_file]
    )
    monkeypatch.setattr(format_tool, "python_module", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        format_tool,
        "run",
        lambda args, *, cwd, check: SimpleNamespace(returncode=1, args=command),
    )

    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        format_tool.main([])

    assert exc_info.value.returncode == 1
    assert exc_info.value.cmd == command


def test_format_skips_missing_python_source_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = tmp_path / "src"
    src.mkdir()
    calls: list[tuple[str, tuple[str, ...]]] = []

    monkeypatch.setattr(format_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(format_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(format_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(format_tool, "iter_markdown_files", lambda _root: [])
    monkeypatch.setattr(
        format_tool,
        "python_module",
        lambda module, *args, cwd, check=True: calls.append((module, args)),
    )

    format_tool.main([])

    assert calls == [
        ("ruff", ("check", "--fix", str(src))),
        ("ruff", ("format", str(src))),
    ]


def test_lint_checks_all_python_source_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ["src", "tests", "scripts"]:
        (tmp_path / name).mkdir()

    calls: list[tuple[str, tuple[str, ...]]] = []

    monkeypatch.setattr(lint_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lint_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(lint_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(lint_tool, "iter_markdown_files", lambda _root: [])
    monkeypatch.setattr(lint_tool, "_pyright_available", lambda _root: False)

    def fake_python_module(
        module: str, *extra_args: str, cwd: Path, check: bool = True
    ) -> None:
        _ = cwd, check
        calls.append((module, extra_args))

    monkeypatch.setattr(lint_tool, "python_module", fake_python_module)

    lint_tool.main(["--skip-tests"])

    assert (
        "compileall",
        (
            "-q",
            str(tmp_path / "src"),
            str(tmp_path / "tests"),
            str(tmp_path / "scripts"),
        ),
    ) in calls
    assert (
        "ruff",
        (
            "check",
            str(tmp_path / "src"),
            str(tmp_path / "tests"),
            str(tmp_path / "scripts"),
        ),
    ) in calls
    assert (
        "ruff",
        (
            "format",
            "--check",
            str(tmp_path / "src"),
            str(tmp_path / "tests"),
            str(tmp_path / "scripts"),
        ),
    ) in calls
    assert (
        "soulmap.devtools.checks.check_markdown_links",
        ("--root", str(tmp_path)),
    ) in calls
    assert (
        "soulmap.devtools.checks.check_markdown_case",
        ("--root", str(tmp_path)),
    ) in calls
    assert not any(module == "isort" for module, _args in calls)


def test_bootstrap_venv_installs_lefthook_in_git_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".git").mkdir()

    commands: list[list[str]] = []

    monkeypatch.setattr(bootstrap_venv, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        bootstrap_venv,
        "_venv_executable",
        lambda _path, name: Path(f"/tmp/{name}"),
    )
    monkeypatch.setattr(bootstrap_venv, "_uv_executable", lambda: "/tmp/uv")
    monkeypatch.setattr(
        bootstrap_venv, "_run", lambda args, *, cwd: commands.append(args)
    )

    assert bootstrap_venv.main([]) == 0

    assert [
        "/tmp/uv",
        "sync",
        "--locked",
        "--python",
        bootstrap_venv.PYTHON_VERSION,
    ] in commands
    assert [str(Path("/tmp/lefthook")), "install"] in commands
    assert "Git hooks installed via lefthook" in capsys.readouterr().out


def test_bootstrap_venv_skips_lefthook_outside_git_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".venv").mkdir()

    commands: list[list[str]] = []

    monkeypatch.setattr(bootstrap_venv, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        bootstrap_venv,
        "_venv_executable",
        lambda _path, name: Path(f"/tmp/{name}"),
    )
    monkeypatch.setattr(bootstrap_venv, "_uv_executable", lambda: "/tmp/uv")
    monkeypatch.setattr(
        bootstrap_venv, "_run", lambda args, *, cwd: commands.append(args)
    )

    assert bootstrap_venv.main([]) == 0

    assert [
        "/tmp/uv",
        "sync",
        "--locked",
        "--python",
        bootstrap_venv.PYTHON_VERSION,
    ] in commands
    assert [str(Path("/tmp/lefthook")), "install"] not in commands
    assert "skipping lefthook install" in capsys.readouterr().out


def test_lefthook_config_replaces_pre_commit_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    config = (repo_root / "lefthook.yml").read_text(encoding="utf-8")

    assert (repo_root / "lefthook.yml").exists()
    assert not (repo_root / ".pre-commit-config.yaml").exists()
    assert "pre-commit:" in config
    assert "parallel: false" in config
    assert "commit-msg:" in config
    assert "uv run ruff check --fix" in config
    assert "uv run ruff format" in config
    assert "uv run soulmap markdown-contract --root ." in config
    assert "uv run soulmap check-links --root ." in config
    assert "uv run soulmap check-case --root ." in config
    assert "uv run pymarkdown --config .pymarkdown.json scan" in config
    assert "uv run cz check --commit-msg-file" in config
    assert "pre-push:" not in config


def test_soulmap_cli_dispatches_test_to_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_python_module(
        module: str, *extra_args: str, cwd: Path, check: bool = True
    ) -> None:
        _ = cwd, check
        calls.append((module, extra_args))

    monkeypatch.setattr(soulmap_cli, "python_module", fake_python_module)

    assert soulmap_cli.main(["test"]) == 0
    assert ("pytest", ("-q",)) in calls


@pytest.mark.parametrize(
    ("wrapper", "implementation"),
    [
        ("build_skill", "soulmap.devtools.packaging.build_skill"),
        ("check_markdown_case", "soulmap.devtools.checks.check_markdown_case"),
        ("check_markdown_links", "soulmap.devtools.checks.check_markdown_links"),
        ("eval_groups", "soulmap.devtools.evals.eval_groups"),
        (
            "eval_markdown_contracts",
            "soulmap.devtools.evals.eval_markdown_contracts",
        ),
        ("eval_responses", "soulmap.devtools.evals.eval_responses"),
        ("format", "soulmap.devtools.quality.format"),
        ("lint", "soulmap.devtools.quality.lint"),
    ],
)
def test_thin_cli_wrapper_forwards_to_implementation_main(
    monkeypatch: pytest.MonkeyPatch, wrapper: str, implementation: str
) -> None:
    implementation_module = importlib.import_module(implementation)
    calls: list[object] = []

    def fake_main(argv: list[str] | None = None) -> int:
        calls.append(argv)
        return 0

    monkeypatch.setattr(implementation_module, "main", fake_main)
    monkeypatch.setattr(sys, "argv", [f"soulmap-{wrapper}", "--sentinel"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module(
            f"soulmap.devtools.cli.{wrapper}",
            run_name="__main__",
        )

    assert exc_info.value.code == 0
    assert calls == [None]


def test_tracked_hygiene_violations_flags_generated_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".git").mkdir()

    class _Result:
        stdout = "\n".join(
            [
                "src/soulmap_ai.dist-info/METADATA",
                "tests/__pycache__/test_example.cpython-311.pyc",
                "src/soulmap/runtime/__init__.py",
            ]
        )

    monkeypatch.setattr(
        "soulmap.devtools.support.repo.subprocess.run",
        lambda *args, **kwargs: _Result(),
    )

    assert tracked_hygiene_violations(tmp_path) == [
        "src/soulmap_ai.dist-info/METADATA",
        "tests/__pycache__/test_example.cpython-311.pyc",
    ]


def test_lint_fails_on_tracked_hygiene_violations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ["src", "tests", "scripts"]:
        (tmp_path / name).mkdir()

    monkeypatch.setattr(lint_tool, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lint_tool, "repo_tooling_lock", _noop_lock)
    monkeypatch.setattr(lint_tool, "python_executable", lambda _root: "python")
    monkeypatch.setattr(lint_tool, "iter_markdown_files", lambda _root: [])
    monkeypatch.setattr(lint_tool, "_pyright_available", lambda _root: False)
    monkeypatch.setattr(
        lint_tool,
        "tracked_hygiene_violations",
        lambda _root: ["src/soulmap_ai.dist-info/METADATA"],
    )
    monkeypatch.setattr(lint_tool, "python_module", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="tracked hygiene violations found"):
        lint_tool.main(["--skip-tests"])
