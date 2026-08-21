from __future__ import annotations

import stat
import zipfile
from pathlib import Path

import pytest

from scripts.verify_artifact_security import (
    ArtifactSecurityError,
    _check_member_path,
    audit_artifact,
    main,
)


def _write_archive(
    path: Path,
    members: dict[str, str | bytes],
    *,
    modes: dict[str, int] | None = None,
) -> Path:
    modes = modes or {}
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in members.items():
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            if name in modes:
                info.external_attr = modes[name] << 16
            archive.writestr(info, content)
    return path


def _safe_archive(tmp_path: Path) -> Path:
    return _write_archive(
        tmp_path / "safe.zip",
        {
            "AGENTS.md": "# Contract\n",
            "SKILL.md": "# Skill\n[Reference](reference/README.md)\n",
            "reference/README.md": "# Reference\n",
        },
    )


def test_audit_accepts_safe_archive(tmp_path: Path) -> None:
    result = audit_artifact(str(_safe_archive(tmp_path)))

    assert result["members"] == 3
    assert result["markdown_links_checked"] == 1


def test_main_reports_pass_for_safe_archive(tmp_path: Path, capsys) -> None:
    path = _safe_archive(tmp_path)

    assert main([str(path)]) == 0
    assert "PASS artifact security" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("members", "match"),
    [
        ({"../escape.md": "bad"}, "unsafe archive member path"),
        ({"AGENTS.md": "-----BEGIN PRIVATE KEY-----"}, "high-confidence secret"),
        ({"AGENTS.md": "<script>alert(1)</script>"}, "dangerous HTML content"),
        ({"AGENTS.md": "[bad](javascript:alert(1))"}, "dangerous URL scheme"),
        ({"AGENTS.md": "[missing](missing.md)"}, "missing relative link"),
        ({"data.json": "not-json"}, "invalid JSON"),
        ({"payload.md": b"PK\x03\x04malicious"}, "executable or nested archive"),
    ],
)
def test_audit_rejects_unsafe_content(
    tmp_path: Path,
    members: dict[str, str | bytes],
    match: str,
) -> None:
    path = _write_archive(tmp_path / "unsafe.zip", members)

    with pytest.raises(ArtifactSecurityError, match=match):
        audit_artifact(str(path))


def test_audit_rejects_symlink_member(tmp_path: Path) -> None:
    path = _write_archive(
        tmp_path / "symlink.zip",
        {"link.md": "AGENTS.md"},
        modes={"link.md": stat.S_IFLNK | 0o777},
    )

    with pytest.raises(ArtifactSecurityError, match="symlink member"):
        audit_artifact(str(path))


def test_audit_rejects_executable_member(tmp_path: Path) -> None:
    path = _write_archive(
        tmp_path / "executable.zip",
        {"payload.md": "content"},
        modes={"payload.md": stat.S_IFREG | 0o755},
    )

    with pytest.raises(ArtifactSecurityError, match="executable permission"):
        audit_artifact(str(path))


def test_audit_rejects_duplicate_member_names(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.zip"
    with (
        pytest.warns(UserWarning, match="Duplicate name"),
        zipfile.ZipFile(path, "w") as archive,
    ):
        archive.writestr("AGENTS.md", "first")
        archive.writestr("AGENTS.md", "second")

    with pytest.raises(ArtifactSecurityError, match="duplicate archive members"):
        audit_artifact(str(path))


@pytest.mark.parametrize(
    "name",
    ["/absolute.md", "C:/absolute.md", "folder\\\\file.md"],
)
def test_member_path_checker_rejects_windows_or_absolute_paths(name: str) -> None:
    with pytest.raises(ArtifactSecurityError, match="unsafe archive member path"):
        _check_member_path(name)
