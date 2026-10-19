"""Shared action input, output, and summary helpers."""

from __future__ import annotations

import os
from pathlib import Path

from errors import GitHubActionError


def env(name: str, *, required: bool = True, default: str = "") -> str:
    """Read and validate an action environment input."""
    value = os.environ.get(name, "")
    if not value:
        value = default
    if required and not value:
        raise GitHubActionError(f"Missing required action input: {name}")
    return value


def boolean(name: str, default: bool = False) -> bool:
    """Read an action input that must contain a boolean value."""
    value = (
        env(
            name,
            required=False,
            default="true" if default else "false",
        )
        .strip()
        .lower()
    )
    if value not in {"true", "false"}:
        raise GitHubActionError(f"Input {name!r} must be true or false.")
    return value == "true"


def repository_parts(repository: str) -> tuple[str, str]:
    """Split and validate a GitHub owner/repository identifier."""
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name:
        raise GitHubActionError(f"Invalid GitHub repository: {repository!r}")
    return owner, name


def write_output(name: str, value: object) -> None:
    """Write an action output using GitHub's multiline protocol."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with Path(output_file).open("a", encoding="utf-8") as handle:
        handle.write(f"{name}<<SOULMAP_EOF\n{value}\nSOULMAP_EOF\n")


def summary(message: str) -> None:
    """Append a message to the GitHub Actions step summary."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with Path(summary_file).open("a", encoding="utf-8") as handle:
            handle.write(f"{message.rstrip()}\n")


def read_body() -> str:
    """Read the release or pull-request body from input or a file."""
    body = env("INPUT_BODY", required=False)
    body_path = env("INPUT_BODY_PATH", required=False)
    if body_path:
        path = Path(body_path)
        if not path.is_file():
            raise GitHubActionError(f"Body file does not exist: {path}")
        body = path.read_text(encoding="utf-8")
    return body


def asset_paths() -> list[Path]:
    """Resolve and validate newline-separated release asset paths."""
    paths: list[Path] = []
    for item in env("INPUT_FILES", required=False).splitlines():
        item = item.strip()
        if item:
            path = Path(item)
            if not path.is_file():
                raise GitHubActionError(f"Release asset does not exist: {path}")
            paths.append(path)
    return paths
