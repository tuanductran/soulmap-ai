from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "block-push-to-main.sh"


def _init_repo(path: Path, branch: str) -> None:
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch", branch, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )


def _run_hook(command: str, repo: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "CODEX_PROJECT_DIR": str(repo),
            "CLAUDE_PROJECT_DIR": str(repo),
        }
    )
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps({"tool_input": {"command": command}}),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )



@pytest.mark.parametrize(
    "command",
    [
        "git push origin main",
        "git push origin HEAD:main",
        "git push origin HEAD:refs/heads/main",
        "git push origin refs/heads/topic:refs/heads/main",
    ],
)
def test_hook_blocks_explicit_main_push_refspecs(tmp_path: Path, command: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_blocks_main_push_through_git_c(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(f"git -C {repo} push origin main", repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "git push",
        "git push origin",
        "git push origin --force",
        "git push origin --dry-run --force",
    ],
)
def test_hook_blocks_implicit_push_from_main(tmp_path: Path, command: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "main")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "protected 'main' branch" in result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "git push origin --all",
        "git push --all origin",
        "git push origin --mirror",
        "git push --mirror origin",
    ],
)
def test_hook_blocks_all_branch_push_modes(tmp_path: Path, command: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "can publish or delete the protected 'main' branch" in result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "git push origin --prune",
        "git push --prune origin",
    ],
)
def test_hook_blocks_pruning_push_modes(tmp_path: Path, command: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "can publish or delete" in result.stderr


def test_hook_blocks_remote_configured_main_refspec(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "config",
            "remote.origin.push",
            "refs/heads/feature:refs/heads/main",
        ],
        check=True,
    )

    result = _run_hook("git push origin", repo)

    assert result.returncode == 2
    assert "protected 'main' branch" in result.stderr


def test_hook_blocks_remote_mirror_configuration(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")
    subprocess.run(
        ["git", "-C", str(repo), "config", "remote.origin.mirror", "true"],
        check=True,
    )

    result = _run_hook("git push origin", repo)

    assert result.returncode == 2
    assert "protected 'main' branch" in result.stderr


def test_hook_expands_environment_variable_in_git_c_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "main")

    result = _run_hook('git -C "$CODEX_PROJECT_DIR" push origin', repo)

    assert result.returncode == 2
    assert "protected 'main' branch" in result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "printf '%s\\n' git push origin",
        "echo git push origin",
        "printf 'git push origin main'",
    ],
)
def test_hook_does_not_match_git_push_text_in_arguments(
    tmp_path: Path, command: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "main")

    result = _run_hook(command, repo)

    assert result.returncode == 0, result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "if git push origin main; then echo pushed; fi",
        "sudo -u deploy git push origin main",
        "bash -c 'git push origin main'",
        'sh -c "git push origin main"',
    ],
)
def test_hook_detects_conditional_and_sudo_wrapped_pushes(
    tmp_path: Path, command: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_detects_git_push_on_a_later_shell_line(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("printf ready\ngit push origin main", repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_detects_push_after_a_comment_line(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("echo ready # note\ngit push origin main", repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_blocks_git_c_implicit_push_from_main(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "main")

    result = _run_hook(f"git -C {repo} push origin", repo)

    assert result.returncode == 2
    assert "protected 'main' branch" in result.stderr



@pytest.mark.parametrize(
    ("branch", "command"),
    [
        ("feature", "git push"),
        ("feature", "git push origin"),
        ("feature", "git push origin feature"),
        ("main", "git push origin feature"),
    ],
)
def test_hook_allows_pushes_that_do_not_target_main(
    tmp_path: Path, branch: str, command: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, branch)

    result = _run_hook(command, repo)

    assert result.returncode == 0, result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "{ git push origin main; }",
        "( git push origin main )",
    ],
)
def test_hook_detects_push_inside_grouped_shell_commands(
    tmp_path: Path, command: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_blocks_branches_alias_for_all_branch_push(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("git push origin --branches", repo)

    assert result.returncode == 2
    assert "can publish or delete" in result.stderr


def test_hook_does_not_treat_push_option_value_as_push_mode(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("git push origin -o --all", repo)

    assert result.returncode == 0, result.stderr



@pytest.mark.parametrize(
    "command",
    [
        "git push origin --signed main",
        "git push origin --signed=yes main",
        "git push origin --signed=no main",
        "git push origin --signed=if-asked main",
    ],
)
def test_hook_detects_main_refspec_after_optional_signed_option(
    tmp_path: Path, command: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(command, repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_blocks_head_refspec_when_current_branch_is_main(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "main")

    result = _run_hook("git push origin HEAD", repo)

    assert result.returncode == 2
    assert "HEAD resolves to the protected 'main' branch" in result.stderr


def test_hook_allows_head_refspec_from_feature_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("git push origin HEAD", repo)

    assert result.returncode == 0, result.stderr


def test_hook_blocks_shell_local_git_c_path_for_implicit_push(tmp_path: Path) -> None:
    root = tmp_path / "root"
    target = tmp_path / "main-checkout"
    root.mkdir()
    target.mkdir()
    _init_repo(root, "feature")
    _init_repo(target, "main")

    result = _run_hook(f'P="{target}"; git -C "$P" push origin', root)

    assert result.returncode == 2
    assert "cannot verify the target repository" in result.stderr


def test_hook_blocks_push_inside_command_substitution(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook('echo "$(git push origin main)"', repo)

    assert result.returncode == 2
    assert "command substitution" in result.stderr


def test_hook_does_not_block_literal_push_text_in_single_quotes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("echo '$(git push origin main)'", repo)

    assert result.returncode == 0, result.stderr


def test_hook_blocks_git_alias_that_pushes_main(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")
    subprocess.run(
        ["git", "-C", str(repo), "config", "alias.ship", "push origin HEAD:main"],
        check=True,
    )

    result = _run_hook("git ship", repo)

    assert result.returncode == 2
    assert "direct push to 'main' is not allowed" in result.stderr


def test_hook_blocks_shell_git_alias_that_may_push(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")
    subprocess.run(
        ["git", "-C", str(repo), "config", "alias.ship", "!git push origin main"],
        check=True,
    )

    result = _run_hook("git ship", repo)

    assert result.returncode == 2
    assert "shell Git alias" in result.stderr


def test_hook_fails_closed_for_implicit_push_with_external_git_dir(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook(
        "git --git-dir=/tmp/other/.git --work-tree=/tmp/other push origin",
        repo,
    )

    assert result.returncode == 2
    assert "cannot verify the target repository" in result.stderr


def test_hook_blocks_chained_git_alias_that_pushes_main(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")
    subprocess.run(
        ["git", "-C", str(repo), "config", "alias.ship", "publish"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "alias.publish", "push origin HEAD:main"],
        check=True,
    )

    result = _run_hook("git ship", repo)

    assert result.returncode == 2
    assert "Git alias chain" in result.stderr


def test_hook_blocks_command_scoped_git_alias_override(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, "feature")

    result = _run_hook("git -c alias.ship='push origin main' ship", repo)

    assert result.returncode == 2
    assert "command-scoped Git aliases" in result.stderr
