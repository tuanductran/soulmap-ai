from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run_hook(
    hook_name: str,
    repo: Path,
    payload: Mapping[str, object],
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
    repo.parent.mkdir(parents=True, exist_ok=True)
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
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
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
    assert "Markdown contract violations detected" in result.stdout
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
    assert "Test failures" in result.stdout
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
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Hook Test"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "hook-test@example.invalid"],
        check=True,
    )
    tracked = repo / "tracked.txt"
    tracked.write_text("committed\\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "fixture commit"],
        check=True,
        capture_output=True,
        text=True,
    )
    (repo / "untracked.txt").write_text("pending\\n", encoding="utf-8")

    result = _run_hook(
        "session-start.sh",
        repo,
        {"cwd": str(repo)},
    )

    assert result.returncode == 0, result.stderr
    assert "Branch:        feature" in result.stdout
    assert "Last commit:" in result.stdout
    assert "fixture commit" in result.stdout
    assert "Uncommitted:   1 file(s) changed" in result.stdout
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
    assert post_tool["matcher"] == "Write|Edit"
    assert len(post_tool["hooks"]) == 4

    expected_timeouts = {
        ".claude/hooks/session-start.sh": 10,
        ".claude/hooks/block-push-to-main.sh": 10,
        ".claude/hooks/post-edit-python.sh": 30,
        ".claude/hooks/post-edit-markdown.sh": 30,
        ".claude/hooks/post-edit-tests.sh": 60,
        ".claude/hooks/post-edit-evals.sh": 60,
    }
    registered_paths: set[str] = set()
    for event_entries in hooks.values():
        for entry in event_entries:
            for hook in entry["hooks"]:
                assert hook["type"] == "command"
                command = hook["command"]
                assert command.startswith('"$CLAUDE_PROJECT_DIR"/')
                relative_path = command.split('"$CLAUDE_PROJECT_DIR"/', 1)[1]
                registered_paths.add(relative_path)
                assert hook["timeout"] == expected_timeouts[relative_path]
                assert (ROOT / relative_path).is_file()

    assert registered_paths == set(expected_timeouts)


def test_pre_tool_push_guard_treats_malformed_payload_as_non_authoritative(
    tmp_path: Path,
) -> None:
    repo = _make_repo(tmp_path)
    result = subprocess.run(
        ["bash", str(ROOT / ".claude" / "hooks" / "block-push-to-main.sh")],
        input="{malformed-json",
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "CODEX_PROJECT_DIR": str(repo),
            "CLAUDE_PROJECT_DIR": str(repo),
        },
        check=False,
    )

    # The hook is defense in depth, not an authorization boundary. GitHub's
    # protected-branch rules remain authoritative if hook input is malformed.
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("hook_name", "relative_path"),
    [
        ("post-edit-python.sh", "src/module.py"),
        ("post-edit-markdown.sh", "docs/guide.md"),
        ("post-edit-tests.sh", "tests/unit/test_sample.py"),
        ("post-edit-evals.sh", "evals/datasets/groups.json"),
    ],
)
)
def test_post_edit_hooks_accept_legacy_codex_payload_when_configured(
    tmp_path: Path,
    hook_name: str,
    relative_path: str,
) -> None:
    repo = _make_repo(tmp_path)
    target = repo / relative_path
    target.parent.mkdir(parents=True)
    target.write_text(
        "{}" if hook_name == "post-edit-evals.sh" else "# sample\\n", encoding="utf-8"
    )
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        hook_name,
        repo,
        {
            "toolName": "edit",
            "toolArgs": json.dumps({"path": relative_path}),
        },
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert call_log.exists()
    calls = call_log.read_text(encoding="utf-8")
    if hook_name == "post-edit-markdown.sh":
        assert f"run soulmap markdown-contract --root {repo}" in calls
    elif hook_name == "post-edit-python.sh":
        assert f"run ruff check --fix {target}" in calls
        assert f"run ruff format {target}" in calls
    elif hook_name == "post-edit-evals.sh":
        assert "run soulmap eval-groups" in calls
    else:
        assert f"run soulmap test {target} --tb=short" in calls


@pytest.mark.parametrize(
    ("hook_name", "deleted_relative_path"),
    [
        ("post-edit-python.sh", "src/deleted.py"),
        ("post-edit-markdown.sh", "docs/deleted.md"),
        ("post-edit-tests.sh", "tests/deleted.py"),
        ("post-edit-evals.sh", "evals/datasets/deleted.json"),
    ],
)
def test_post_edit_hooks_ignore_malformed_payload_and_deleted_files(
    tmp_path: Path,
    hook_name: str,
    deleted_relative_path: str,
) -> None:
    repo = _make_repo(tmp_path)
    deleted = repo / deleted_relative_path
    fake_bin, call_log = _fake_uv(tmp_path)

    malformed = subprocess.run(
        ["bash", str(ROOT / ".claude" / "hooks" / hook_name)],
        input="{malformed-json",
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "CODEX_PROJECT_DIR": str(repo),
            "CLAUDE_PROJECT_DIR": str(repo),
            "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
            "HOOK_CALL_LOG": str(call_log),
        },
        check=False,
    )
    assert malformed.returncode == 0, malformed.stderr
    assert not call_log.exists()

    deleted_payload = {"tool_input": {"file_path": str(deleted)}}
    missing = _run_hook(
        hook_name,
        repo,
        deleted_payload,
        fake_bin=fake_bin,
        call_log=call_log,
    )
    assert missing.returncode == 0, missing.stderr
    assert not call_log.exists()


@pytest.mark.parametrize(
    ("hook_name", "relative_path"),
    [
        ("post-edit-markdown.sh", "docs/guide.md"),
        ("post-edit-tests.sh", "tests/unit/test_sample.py"),
    ],
)
def test_post_edit_hooks_reject_relative_traversal(
    tmp_path: Path,
    hook_name: str,
    relative_path: str,
) -> None:
    repo = _make_repo(tmp_path)
    outside = tmp_path / relative_path
    outside.parent.mkdir(parents=True)
    outside.write_text("# outside\n", encoding="utf-8")
    fake_bin, call_log = _fake_uv(tmp_path)

    result = _run_hook(
        hook_name,
        repo,
        {"tool_input": {"file_path": f"../{relative_path}"}},
        fake_bin=fake_bin,
        call_log=call_log,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()


def test_post_edit_python_reports_ruff_failures_without_blocking(
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
        hook_exit="1",
    )

    assert result.returncode == 0, result.stderr
    assert "stub diagnostic" in result.stdout
    assert call_log.read_text(encoding="utf-8").splitlines() == [
        f"run ruff check --fix {target}",
        f"run ruff format {target}",
    ]


def test_session_start_prefers_event_cwd_over_project_environment(
    tmp_path: Path,
) -> None:
    cwd_parent = tmp_path / "cwd"
    cwd_parent.mkdir()
    cwd_repo = _make_repo(cwd_parent)

    fallback_parent = tmp_path / "fallback"
    fallback_parent.mkdir()
    fallback_repo = _make_repo(fallback_parent)
    subprocess.run(
        ["git", "-C", str(fallback_repo), "branch", "-m", "fallback"],
        check=True,
    )

    env = os.environ.copy()
    env.update(
        {
            "CODEX_PROJECT_DIR": str(fallback_repo),
            "CLAUDE_PROJECT_DIR": str(fallback_repo),
        }
    )
    result = subprocess.run(
        ["bash", str(ROOT / ".claude" / "hooks" / "session-start.sh")],
        input=json.dumps({"cwd": str(cwd_repo)}),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Branch:        feature" in result.stdout
    assert "Branch:        fallback" not in result.stdout


@pytest.mark.parametrize(
    ("hook_name", "relative_path", "expected_calls"),
    [
        (
            "post-edit-python.sh",
            "src/module.py",
            ("run ruff check --fix", "run ruff format"),
        ),
        (
            "post-edit-markdown.sh",
            "docs/guide.md",
            ("run soulmap markdown-contract --root",),
        ),
        (
            "post-edit-tests.sh",
            "tests/test_sample.py",
            ("run soulmap test",),
        ),
        (
            "post-edit-evals.sh",
            "evals/datasets/groups.json",
            ("run soulmap eval-groups",),
        ),
    ],
)
def test_post_edit_hooks_resolve_repo_from_hook_location_without_environment(
    tmp_path: Path,
    hook_name: str,
    relative_path: str,
    expected_calls: tuple[str, ...],
) -> None:
    repo = _make_repo(tmp_path)
    target = repo / relative_path
    target.parent.mkdir(parents=True)
    fixture = (
        "# sample\n"
        if target.suffix == ".md"
        else "{}\n"
        if target.suffix == ".json"
        else "value = 1\n"
    )
    target.write_text(fixture, encoding="utf-8")

    hook_copy = repo / ".claude" / "hooks" / hook_name
    hook_copy.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".claude" / "hooks" / hook_name, hook_copy)

    fake_bin, call_log = _fake_uv(tmp_path)
    env = os.environ.copy()
    env.pop("CODEX_PROJECT_DIR", None)
    env.pop("CLAUDE_PROJECT_DIR", None)
    env.update(
        {
            "PATH": f"{fake_bin}{os.pathsep}{env.get('PATH', '')}",
            "HOOK_CALL_LOG": str(call_log),
        }
    )
    result = subprocess.run(
        ["bash", str(hook_copy)],
        input=json.dumps({"tool_input": {"file_path": str(target)}}),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    calls = call_log.read_text(encoding="utf-8").splitlines()
    assert len(calls) == len(expected_calls)
    for call, expected in zip(calls, expected_calls, strict=True):
        assert call.startswith(expected)
    assert str(repo) in " ".join(calls)


@pytest.mark.parametrize(
    ("hook_name", "relative_path", "fixture"),
    [
        ("post-edit-python.sh", "src/module.py", "value = 1\\n"),
        ("post-edit-markdown.sh", "docs/guide.md", "# external\\n"),
        (
            "post-edit-tests.sh",
            "tests/test_external.py",
            "def test_external(): pass\n",
        ),
        ("post-edit-evals.sh", "evals/datasets/groups.json", "{}\\n"),
    ],
)
def test_post_edit_hooks_do_not_trust_external_git_repo_without_project_env(
    tmp_path: Path,
    hook_name: str,
    relative_path: str,
    fixture: str,
) -> None:
    repo = _make_repo(tmp_path / "workspace")
    hook_copy = repo / ".claude" / "hooks" / hook_name
    hook_copy.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".claude" / "hooks" / hook_name, hook_copy)

    external_repo = _make_repo(tmp_path / "external")
    target = external_repo / relative_path
    target.parent.mkdir(parents=True)
    target.write_text(fixture, encoding="utf-8")

    fake_bin, call_log = _fake_uv(tmp_path)
    env = os.environ.copy()
    env.pop("CODEX_PROJECT_DIR", None)
    env.pop("CLAUDE_PROJECT_DIR", None)
    env.update(
        {
            "PATH": f"{fake_bin}{os.pathsep}{env.get('PATH', '')}",
            "HOOK_CALL_LOG": str(call_log),
        }
    )
    result = subprocess.run(
        ["bash", str(hook_copy)],
        input=json.dumps({"tool_input": {"file_path": str(target)}}),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not call_log.exists()
