from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_hook(
    hook_name: str,
    repo: Path,
    payload: dict[str, object],
    *,
    fake_bin: Path | None = None,
    call_log: Path | None = None,
    hook_exit: str = "0",
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "CODEX_PROJECT_DIR": str(repo),
            "CLAUDE_PROJECT_DIR": str(repo),
            "HOOK_EXIT": hook_exit,
        }
    )
    if fake_bin is not None:
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    if call_log is not None:
        env["HOOK_CALL_LOG"] = str(call_log)
    return subprocess.run(
        ["bash", str(ROOT / ".claude" / "hooks" / hook_name)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def _fake_uv(tmp_path: Path) -> tuple[Path, Path]:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    uv = fake_bin / "uv"
    uv.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$*" >> "$HOOK_CALL_LOG"\n'
        'printf "stub diagnostic\\n"\n'
        'exit "${HOOK_EXIT:-0}"\n',
        encoding="utf-8",
    )
    uv.chmod(0o755)
    return fake_bin, tmp_path / "uv-calls.txt"


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch", "feature", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    return repo


def test_post_edit_python_formats_only_existing_in_repo_python_files(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    target = repo / "src" / "module.py"
    target.parent.mkdir()
    target.write_text("value=1\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-python.sh",
        repo,
        {"tool_input": {"file_path": str(target)}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert call_log.read_text(encoding="utf-8").splitlines() == [
        f"run ruff check --fix {target}",
        f"run ruff format {target}",
    ]


def test_post_edit_python_rejects_absolute_path_outside_repository(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("value=1\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-python.sh",
        repo,
        {"tool_input": {"file_path": str(outside)}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()
    assert outside.read_text(encoding="utf-8") == "value=1\n"


def test_post_edit_python_rejects_relative_path_traversal(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("value=1\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-python.sh",
        repo,
        {"tool_input": {"file_path": "src/../../outside.py"}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()
    assert outside.read_text(encoding="utf-8") == "value=1\n"


def test_post_edit_python_rejects_symlink_that_escapes_repository(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("value=1\n", encoding="utf-8")
    src = repo / "src"
    src.mkdir()
    link = src / "linked.py"
    link.symlink_to(outside)
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-python.sh",
        repo,
        {"tool_input": {"file_path": str(link)}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()


def test_post_edit_markdown_reports_contract_failure_without_blocking(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    target = repo / "docs" / "guide.md"
    target.parent.mkdir()
    target.write_text("# Guide\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-markdown.sh",
        repo,
        {"tool_input": {"file_path": str(target)}},
        fake_bin=fake_bin,
        call_log=call_log,
        hook_exit="1",
    )

    assert result.returncode == 0, result.stderr
    assert "Contract violations detected" in result.stdout
    assert "stub diagnostic" in result.stdout
    assert call_log.read_text(encoding="utf-8").splitlines() == [
        f"run soulmap markdown-contract --root {repo}"
    ]


def test_post_edit_markdown_ignores_path_outside_repository(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-markdown.sh",
        repo,
        {"tool_input": {"file_path": str(outside)}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()


def test_post_edit_tests_runs_only_repo_test_and_remains_non_blocking(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    target = repo / "tests" / "unit" / "test_sample.py"
    target.parent.mkdir(parents=True)
    target.write_text("def test_sample(): pass\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-tests.sh",
        repo,
        {"tool_input": {"file_path": str(target)}},
        fake_bin=fake_bin,
        call_log=call_log,
        hook_exit="1",
    )

    assert result.returncode == 0, result.stderr
    assert "Tests failed" in result.stdout
    assert "stub diagnostic" in result.stdout
    assert call_log.read_text(encoding="utf-8").splitlines() == [
        f"run soulmap test {target} --tb=short"
    ]


def test_post_edit_tests_rejects_external_test_file(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    outside = tmp_path / "tests" / "test_outside.py"
    outside.parent.mkdir()
    outside.write_text("raise RuntimeError('must not execute')\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        "post-edit-tests.sh",
        repo,
        {"tool_input": {"file_path": str(outside)}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()


def test_session_start_emits_repo_branch_and_workflow_context(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)

    result = _run_hook(
        "session-start.sh",
        repo,
        {"cwd": str(repo)},
    )

    assert result.returncode == 0, result.stderr
    assert "Branch:        feature" in result.stdout
    assert "SoulMap AI - Repo Context" in result.stdout
    assert "Never push directly to main" in result.stdout


def test_session_start_is_safe_outside_git_repository(tmp_path: Path) -> None:
    outside = tmp_path / "not-a-repository"
    outside.mkdir()

    result = subprocess.run(
        ["bash", str(ROOT / ".claude" / "hooks" / "session-start.sh")],
        input=json.dumps({"cwd": str(outside)}),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Branch:        unknown" in result.stdout


def test_claude_settings_hook_contract_and_command_paths() -> None:
    settings = json.loads(
        (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    hooks = settings["hooks"]

    assert set(hooks) == {"SessionStart", "PreToolUse", "PostToolUse"}

    session_hooks = hooks["SessionStart"][0]["hooks"]
    assert len(session_hooks) == 1
    assert session_hooks[0]["timeout"] == 10

    pre_tool = hooks["PreToolUse"][0]
    assert pre_tool["matcher"] == "Bash"
    assert len(pre_tool["hooks"]) == 1
    assert pre_tool["hooks"][0]["timeout"] == 10

    post_tool = hooks["PostToolUse"][0]
    assert post_tool["matcher"] == "Write|Edit|MultiEdit"
    assert len(post_tool["hooks"]) == 4

    registered_paths: set[str] = set()
    for event_entries in hooks.values():
        for entry in event_entries:
            for hook in entry["hooks"]:
                assert hook["type"] == "command"
                assert hook["timeout"] > 0
                command = hook["command"]
                assert command.startswith('"$CLAUDE_PROJECT_DIR"/')
                relative_path = command.split('"$CLAUDE_PROJECT_DIR"/', 1)[1]
                registered_paths.add(relative_path)
                assert (ROOT / relative_path).is_file()

    assert registered_paths == {
        ".claude/hooks/session-start.sh",
        ".claude/hooks/block-push-to-main.sh",
        ".claude/hooks/post-edit-python.sh",
        ".claude/hooks/post-edit-markdown.sh",
        ".claude/hooks/post-edit-tests.sh",
        ".claude/hooks/post-edit-evals.sh",
    }
