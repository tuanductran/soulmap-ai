from __future__ import annotations

import importlib
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from soulmap.devtools.support import markdown as markdown_support
from soulmap.devtools.support import run as run_support


def _reset_venv_notice() -> None:
    function = cast(Any, run_support.python_executable)
    function._venv_notice_printed = False


def test_python_executable_prefers_local_venv_and_prints_one_notice(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    local_python = tmp_path / ".venv" / "bin" / "python"
    local_python.parent.mkdir(parents=True)
    local_python.touch()
    _reset_venv_notice()
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(run_support.sys, "executable", "/usr/bin/python")

    assert run_support.python_executable(tmp_path) == str(local_python)
    assert run_support.python_executable(tmp_path) == str(local_python)

    stderr = capsys.readouterr().err
    assert stderr.count("detected local .venv") == 1


def test_python_executable_respects_active_venv_and_ci(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _reset_venv_notice()
    monkeypatch.setattr(run_support.sys, "executable", "/active/python")
    monkeypatch.setenv("VIRTUAL_ENV", "/active")

    assert run_support.python_executable(tmp_path) == "/active/python"
    assert capsys.readouterr().err == ""

    monkeypatch.delenv("VIRTUAL_ENV")
    monkeypatch.setenv("CI", "true")
    assert run_support.python_executable(tmp_path) == "/active/python"
    assert capsys.readouterr().err == ""


def test_run_merges_environment_and_python_module_delegates(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_subprocess_run(
        args: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(run_support.subprocess, "run", fake_subprocess_run)
    monkeypatch.setattr(run_support, "python_executable", lambda _root: "/venv/python")

    result = run_support.run(
        ["tool", "arg"],
        cwd=tmp_path,
        env={"SOULMAP_TEST": "1"},
        check=False,
    )
    run_support.python_module("pytest", "-q", cwd=tmp_path)

    assert result.returncode == 0
    assert calls[0][0] == ["tool", "arg"]
    assert calls[0][1]["cwd"] == str(tmp_path)
    assert cast(dict[str, str], calls[0][1]["env"])["SOULMAP_TEST"] == "1"
    assert calls[0][1]["text"] is True
    assert calls[0][1]["check"] is False
    assert calls[1][0] == ["/venv/python", "-m", "pytest", "-q"]
    assert calls[1][1]["check"] is True


def test_markdown_file_collection_and_input_resolution(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "dist").mkdir()
    root_file = tmp_path / "README.md"
    docs_file = tmp_path / "docs" / "guide.md"
    root_file.write_text("# Root\n", encoding="utf-8")
    docs_file.write_text("# Guide\n", encoding="utf-8")
    (tmp_path / ".git" / "ignored.md").write_text("# Ignored\n", encoding="utf-8")
    (tmp_path / "dist" / "ignored.md").write_text("# Ignored\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("notes\n", encoding="utf-8")

    assert set(markdown_support.iter_markdown_files(tmp_path)) == {
        root_file,
        docs_file,
    }
    assert set(
        markdown_support.resolve_markdown_inputs(
            tmp_path,
            ["docs", "docs/guide.md", "README.md", "notes.txt", "missing.md"],
        )
    ) == {root_file.resolve(), docs_file}


def test_markdown_parsing_slug_anchor_and_reference_helpers() -> None:
    front_matter = ["---", "# note", "name: 'soulmap'", 'description: "Guide"', "---"]
    lines = [
        "# Alpha *Title*\n",
        "\n",
        "## Alpha *Title*\n",
        "\n",
        "```md\n",
        "# Ignored heading\n",
        "[Ignored](missing.md)\n",
        "```\n",
        "[Guide](docs/guide.md#alpha-title)\n",
        "![Logo](assets/logo.png)\n",
    ]

    assert markdown_support.parse_yaml_front_matter(front_matter) == {
        "name": "soulmap",
        "description": "Guide",
    }
    assert markdown_support.parse_yaml_front_matter(["name: missing delimiter"]) is None
    assert (
        markdown_support.parse_yaml_front_matter(["---", "name: missing end"]) is None
    )
    assert (
        markdown_support.strip_inline_markup("[A *link*](target) <em>here</em>")
        == "A link here"
    )
    assert markdown_support.slugify_github_anchor("Alpha *Title*!") == "alpha-title"
    assert markdown_support.extract_heading_anchors(lines) == [
        markdown_support.MarkdownHeadingAnchor("alpha-title", "Alpha *Title*", 1),
        markdown_support.MarkdownHeadingAnchor("alpha-title-1", "Alpha *Title*", 3),
    ]
    assert markdown_support.iter_markdown_references(lines) == [
        markdown_support.MarkdownReference(9, "Guide", "docs/guide.md#alpha-title"),
        markdown_support.MarkdownReference(
            10, "Logo", "assets/logo.png", is_image=True
        ),
    ]


def test_fence_tracker_requires_matching_marker_and_length_to_close() -> None:
    lines = [
        "# Title\n",
        "\n",
        "````markdown\n",
        "Nested example fence:\n",
        "\n",
        "```python\n",
        "x = 1\n",
        "```\n",
        "\n",
        "The inner triple-backtick fence must not close the outer one.\n",
        "````\n",
        "\n",
        "## Real heading after\n",
    ]

    assert markdown_support.extract_heading_anchors(lines) == [
        markdown_support.MarkdownHeadingAnchor("title", "Title", 1),
        markdown_support.MarkdownHeadingAnchor(
            "real-heading-after", "Real heading after", 13
        ),
    ]

    tracker = markdown_support.FenceTracker()
    assert tracker.consume("plain text\n") is False
    assert tracker.consume("```\n") is True
    assert tracker.in_fence is True
    # A mismatched marker char does not close the fence, only content inside it.
    assert tracker.consume("~~~\n") is True
    assert tracker.in_fence is True
    assert tracker.consume("```\n") is True
    assert tracker.in_fence is False


def test_markdown_target_helpers_handle_fragments_external_and_local_paths(
    tmp_path: Path,
) -> None:
    current = tmp_path / "docs" / "current.md"
    current.parent.mkdir()
    current.touch()

    assert markdown_support.split_markdown_link_target(" <docs/guide.md#details> ") == (
        "docs/guide.md",
        "details",
    )
    assert markdown_support.split_markdown_link_target("#details") == ("", "details")
    assert markdown_support.split_markdown_link_target("docs/guide.md") == (
        "docs/guide.md",
        None,
    )
    assert markdown_support.is_external_markdown_target("HTTPS://example.com")
    assert markdown_support.is_external_markdown_target("mailto:test@example.com")
    assert not markdown_support.is_external_markdown_target("docs/guide.md")
    assert (
        markdown_support.resolve_local_markdown_target(
            repo_root=tmp_path,
            current_file=current,
            target_path="../notes%20file.md",
        )
        == (tmp_path / "notes file.md").resolve()
    )
    assert (
        markdown_support.resolve_local_markdown_target(
            repo_root=tmp_path,
            current_file=current,
            target_path="/README.md",
        )
        == (tmp_path / "README.md").resolve()
    )
    assert (
        markdown_support.resolve_local_markdown_target(
            repo_root=tmp_path,
            current_file=current,
            target_path="",
        )
        == current.resolve()
    )


def test_python_executable_warns_once_without_venv_or_ci(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _reset_venv_notice()
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(run_support.sys, "executable", "/system/python")

    assert run_support.python_executable(tmp_path) == "/system/python"
    assert run_support.python_executable(tmp_path) == "/system/python"

    assert capsys.readouterr().err.count("warning: no local `.venv` detected") == 1


@pytest.mark.skipif(os.name == "nt", reason="exercise the POSIX flock branch")
def test_repo_tooling_lock_waits_then_cleans_root_lock(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    fcntl = importlib.import_module("fcntl")
    attempts = 0
    sleep_calls: list[float] = []
    times = iter([0.0, 0.6])

    def fake_flock(_fd: int, flags: int) -> None:
        nonlocal attempts
        if flags & fcntl.LOCK_UN:
            return
        attempts += 1
        if attempts == 1:
            raise OSError("busy")

    monkeypatch.setattr(fcntl, "flock", fake_flock)
    monkeypatch.setattr(run_support.time, "monotonic", lambda: next(times))
    monkeypatch.setattr(
        run_support.time, "sleep", lambda delay: sleep_calls.append(delay)
    )

    with run_support.repo_tooling_lock(tmp_path, name="test", poll_interval_s=0.02):
        assert (tmp_path / ".test.lock").exists()

    assert attempts == 2
    assert sleep_calls == [0.02]
    assert "waiting for repo tooling lock .test.lock" in capsys.readouterr().err
    assert not (tmp_path / ".test.lock").exists()


def test_repo_tooling_lock_uses_windows_venv_lock_and_unlocks(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / ".venv").mkdir()
    lock_modes: list[int] = []

    class _Msvcrt:
        LK_NBLCK = 1
        LK_UNLCK = 2

        @staticmethod
        def locking(_fd: int, mode: int, _size: int) -> None:
            lock_modes.append(mode)

    monkeypatch.setattr(run_support, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(run_support, "msvcrt", _Msvcrt, raising=False)

    with run_support.repo_tooling_lock(tmp_path, name="windows"):
        assert (tmp_path / ".venv" / ".windows.lock").exists()

    assert lock_modes == [_Msvcrt.LK_NBLCK, _Msvcrt.LK_UNLCK]
    assert not (tmp_path / ".venv" / ".windows.lock").exists()


def test_repo_tooling_lock_tolerates_missing_or_unremovable_cleanup_file(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    original_unlink = Path.unlink

    def missing_unlink(path: Path, missing_ok: bool = False) -> None:
        if path.name == ".missing.lock":
            raise FileNotFoundError
        if path.name == ".stuck.lock":
            raise OSError("busy")
        original_unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", missing_unlink)

    with run_support.repo_tooling_lock(tmp_path, name="missing"):
        pass
    with run_support.repo_tooling_lock(tmp_path, name="stuck"):
        pass

    assert (
        "warning: failed to remove repo tooling lock .stuck.lock: busy"
        in capsys.readouterr().err
    )


@pytest.mark.skipif(os.name == "nt", reason="exercise the POSIX flock branch")
def test_repo_tooling_lock_retries_before_waiting_notice(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    fcntl = importlib.import_module("fcntl")
    attempts = 0
    sleep_calls: list[float] = []
    times = iter([0.0, 0.4])

    def fake_flock(_fd: int, flags: int) -> None:
        nonlocal attempts
        if flags & fcntl.LOCK_UN:
            return
        attempts += 1
        if attempts == 1:
            raise OSError("busy")

    monkeypatch.setattr(fcntl, "flock", fake_flock)
    monkeypatch.setattr(run_support.time, "monotonic", lambda: next(times))
    monkeypatch.setattr(
        run_support.time,
        "sleep",
        lambda delay: sleep_calls.append(delay),
    )

    with run_support.repo_tooling_lock(tmp_path, name="quiet", poll_interval_s=0.01):
        pass

    assert attempts == 2
    assert sleep_calls == [0.01]
    assert capsys.readouterr().err == ""


def test_markdown_references_use_commonmark_tokens_for_edge_cases() -> None:
    lines = [
        'Reference [guide][g] and [nested](docs/(inner).md "title").',
        "",
        '![Logo](assets/logo.png "caption")',
        "",
        "[g]: docs/guidance.md#inner-knowing",
        "",
        "```md",
        "[Ignored](missing.md)",
        "```",
    ]

    assert markdown_support.iter_markdown_references(lines) == [
        markdown_support.MarkdownReference(
            1, "guide", "docs/guidance.md#inner-knowing"
        ),
        markdown_support.MarkdownReference(1, "nested", "docs/(inner).md"),
        markdown_support.MarkdownReference(3, "Logo", "assets/logo.png", is_image=True),
    ]
