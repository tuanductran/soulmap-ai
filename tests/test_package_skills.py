"""Tests for packaging skill markdown into generated artifacts."""

import hashlib
import json
from pathlib import Path

import pytest

from modules.package_skills import package_skills_to_markdown


def test_package_skills_respects_ignore_and_writes_log(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "alpha.md").write_text("# Alpha\nA — B\n", encoding="utf-8")
    (skills_dir / "beta.md").write_text("# Beta\nKeep me out.\n", encoding="utf-8")

    ignore_file = tmp_path / ".skillsignore"
    ignore_file.write_text("beta.md\n", encoding="utf-8")

    output_file = skills_dir / "AGENTS.md"
    log_file = skills_dir / "AGENTS.sources.jsonl"

    package_skills_to_markdown(
        skills_dir,
        output_file,
        ignore_file=ignore_file,
        log_file=log_file,
    )

    bundled = output_file.read_text(encoding="utf-8")
    assert bundled.startswith("# AGENTS.md\n")
    assert "\n## Alpha\n" in bundled
    assert "A — B" in bundled
    assert "\n## Beta\n" not in bundled
    assert "\n## Table of contents\n" in bundled
    assert "- [Alpha](#alpha)" in bundled

    entries = [
        json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()
    ]
    assert entries == [
        {
            "path": "alpha.md",
            "bytes": len("# Alpha\nA — B\n".encode()),
            "sha256": hashlib.sha256("# Alpha\nA — B\n".encode()).hexdigest(),
        }
    ]


def test_package_skills_skips_missing_directory(tmp_path: Path, capsys) -> None:
    output_file = tmp_path / "AGENTS.md"

    with pytest.raises(FileNotFoundError):
        package_skills_to_markdown(tmp_path / "missing", output_file)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert not output_file.exists()
