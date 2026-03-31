from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from soulmap_devtools.cli import bootstrap_venv
from soulmap_devtools.quality import format as format_tool
from soulmap_devtools.quality import lint as lint_tool
from soulmap_devtools.support import repo as repo_support
from soulmap_devtools.support.repo import (
    python_source_paths,
    tracked_hygiene_violations,
)


@contextmanager
def _noop_lock(_repo_root: Path):
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
    tmp_path: Path, monkeypatch
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
        / "soulmap_devtools"
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


def test_format_relies_on_ruff_for_python_rewrites(tmp_path: Path, monkeypatch) -> None:
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


def test_lint_checks_all_python_source_paths(tmp_path: Path, monkeypatch) -> None:
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
        "soulmap_devtools.cli.check_markdown_links",
        ("--root", str(tmp_path)),
    ) in calls
    assert (
        "soulmap_devtools.cli.check_markdown_case",
        ("--root", str(tmp_path)),
    ) in calls
    assert not any(module == "isort" for module, _args in calls)


def test_bootstrap_venv_installs_lefthook_in_git_repo(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".git").mkdir()

    commands: list[list[str]] = []

    monkeypatch.setattr(bootstrap_venv, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        bootstrap_venv, "_venv_python", lambda _path: Path("/tmp/python")
    )
    monkeypatch.setattr(
        bootstrap_venv,
        "_venv_executable",
        lambda _path, name: Path(f"/tmp/{name}"),
    )
    monkeypatch.setattr(
        bootstrap_venv, "_run", lambda args, *, cwd: commands.append(args)
    )

    assert bootstrap_venv.main([]) == 0

    assert [str(Path("/tmp/lefthook")), "install"] in commands
    assert "Git hooks installed via lefthook" in capsys.readouterr().out


def test_bootstrap_venv_skips_lefthook_outside_git_repo(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    (tmp_path / ".venv").mkdir()

    commands: list[list[str]] = []

    monkeypatch.setattr(bootstrap_venv, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        bootstrap_venv, "_venv_python", lambda _path: Path("/tmp/python")
    )
    monkeypatch.setattr(
        bootstrap_venv,
        "_venv_executable",
        lambda _path, name: Path(f"/tmp/{name}"),
    )
    monkeypatch.setattr(
        bootstrap_venv, "_run", lambda args, *, cwd: commands.append(args)
    )

    assert bootstrap_venv.main([]) == 0

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
    assert "python -m ruff check --fix" in config
    assert "python -m ruff format" in config
    assert "python -m soulmap_runtime.guards.markdown_contract --root ." in config
    assert "python -m soulmap_devtools.cli.check_markdown_links --root ." in config
    assert "python -m soulmap_devtools.cli.check_markdown_case --root ." in config
    assert "python -m pymarkdown --config .pymarkdown.json scan" in config
    assert "python -m commitizen check --commit-msg-file" in config
    assert "pre-push:" not in config


def test_tracked_hygiene_violations_flags_generated_paths(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / ".git").mkdir()

    class _Result:
        stdout = "\n".join(
            [
                "src/soulmap_ai.dist-info/METADATA",
                "tests/__pycache__/test_example.cpython-311.pyc",
                "src/soulmap_runtime/__init__.py",
            ]
        )

    monkeypatch.setattr(
        "soulmap_devtools.support.repo.subprocess.run",
        lambda *args, **kwargs: _Result(),
    )

    assert tracked_hygiene_violations(tmp_path) == [
        "src/soulmap_ai.dist-info/METADATA",
        "tests/__pycache__/test_example.cpython-311.pyc",
    ]


def test_lint_fails_on_tracked_hygiene_violations(tmp_path: Path, monkeypatch) -> None:
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

    try:
        lint_tool.main(["--skip-tests"])
    except RuntimeError as exc:
        assert "tracked hygiene violations found" in str(exc)
    else:
        raise AssertionError("Expected lint to fail on tracked hygiene violations")
