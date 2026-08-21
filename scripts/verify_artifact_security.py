"""Run security checks against generated SoulMap distribution archives."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import stat
import sys
import zipfile
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

DEFAULT_ARTIFACTS = ("dist/soulmap-ai.zip", "dist/soulmap-ai.skill")
MAX_MEMBER_SIZE = 1024 * 1024
MAX_COMPRESSION_RATIO = 100
DANGEROUS_URL_SCHEMES = {"javascript", "data", "file", "vbscript"}
EXECUTABLE_SIGNATURES = {
    b"\x7fELF": "ELF",
    b"MZ": "PE/Windows",
    b"#!": "shebang",
    b"PK\x03\x04": "nested ZIP",
    b"\x1f\x8b": "gzip",
}
HIGH_CONFIDENCE_SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github-token": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
    ),
    "slack-token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "openai-style-key": re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)")
DANGEROUS_HTML_PATTERNS = {
    "script-tag": re.compile(r"<\s*script\b", re.IGNORECASE),
    "embedded-content": re.compile(r"<\s*(?:iframe|object|embed)\b", re.IGNORECASE),
    "inline-event-handler": re.compile(
        r"\bon(?:error|load|click|mouseover)\s*=", re.IGNORECASE
    ),
}


class ArtifactSecurityError(ValueError):
    """Raised when an artifact fails a security check."""


def _member_mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0xFFFF


def _check_member_path(name: str) -> None:
    parsed = PurePosixPath(name)
    if (
        not name
        or "\x00" in name
        or "\\" in name
        or name.startswith("/")
        or name.startswith("\\")
        or (len(name) >= 2 and name[1] == ":")
        or ".." in parsed.parts
    ):
        raise ArtifactSecurityError(f"unsafe archive member path: {name!r}")


def _check_member_metadata(info: zipfile.ZipInfo) -> None:
    name = info.filename
    mode = _member_mode(info)
    file_type = stat.S_IFMT(mode)
    if file_type == stat.S_IFLNK:
        raise ArtifactSecurityError(f"symlink member: {name!r}")
    if file_type not in (0, stat.S_IFREG, stat.S_IFDIR) and not info.is_dir():
        raise ArtifactSecurityError(f"special file member: {name!r} mode={mode:o}")
    if not info.is_dir() and stat.S_IMODE(mode) & 0o111:
        raise ArtifactSecurityError(f"executable permission on member: {name!r}")
    if info.file_size and not info.compress_size:
        raise ArtifactSecurityError(f"invalid compressed size for member: {name!r}")
    if info.file_size > MAX_MEMBER_SIZE:
        raise ArtifactSecurityError(
            f"member exceeds {MAX_MEMBER_SIZE} bytes: {name!r} ({info.file_size})"
        )
    if (
        info.compress_size
        and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO
    ):
        raise ArtifactSecurityError(
            f"compression ratio exceeds {MAX_COMPRESSION_RATIO}: {name!r}"
        )


def _check_content(name: str, data: bytes) -> None:
    for signature, label in EXECUTABLE_SIGNATURES.items():
        if data.startswith(signature):
            raise ArtifactSecurityError(
                f"executable or nested archive signature in {name!r}: {label}"
            )

    text = data.decode("utf-8", errors="strict")
    for label, pattern in DANGEROUS_HTML_PATTERNS.items():
        if pattern.search(text):
            raise ArtifactSecurityError(f"dangerous HTML content in {name!r}: {label}")

    for label, pattern in HIGH_CONFIDENCE_SECRET_PATTERNS.items():
        if pattern.search(text):
            raise ArtifactSecurityError(
                f"possible high-confidence secret in {name!r}: {label}"
            )

    if name.endswith(".json"):
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            raise ArtifactSecurityError(f"invalid JSON in {name!r}: {exc}") from exc


def _check_links(name: str, text: str, names: set[str]) -> int:
    checked = 0
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip('<>"')
        parts = urlsplit(target)
        checked += 1
        if parts.scheme:
            if parts.scheme.lower() in DANGEROUS_URL_SCHEMES:
                raise ArtifactSecurityError(
                    f"dangerous URL scheme in {name!r}: {target!r}"
                )
            continue
        if target.startswith("/"):
            raise ArtifactSecurityError(f"absolute local link in {name!r}: {target!r}")
        relative = unquote(parts.path)
        if not relative:
            continue
        candidate = posixpath.normpath(
            posixpath.join(posixpath.dirname(name), relative)
        )
        if candidate == ".." or candidate.startswith("../"):
            raise ArtifactSecurityError(
                f"link escapes artifact in {name!r}: {target!r}"
            )
        if candidate not in names and not any(
            member.startswith(candidate.rstrip("/") + "/") for member in names
        ):
            raise ArtifactSecurityError(
                f"missing relative link in {name!r}: {target!r} -> {candidate!r}"
            )
    return checked


def audit_artifact(path: str) -> dict[str, Any]:
    """Audit one archive without extracting or executing its contents."""
    archive_path = path
    try:
        archive = zipfile.ZipFile(archive_path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ArtifactSecurityError(
            f"cannot open ZIP archive {archive_path!r}: {exc}"
        ) from exc

    with archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ArtifactSecurityError(f"duplicate archive members: {duplicates}")
        for info in infos:
            _check_member_path(info.filename)
            _check_member_metadata(info)

        checked_links = 0
        for info in infos:
            if info.is_dir():
                continue
            try:
                data = archive.read(info)
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                raise ArtifactSecurityError(
                    f"CRC/read failure in {info.filename!r}: {exc}"
                ) from exc
            _check_content(info.filename, data)
            if info.filename.endswith(".md"):
                checked_links += _check_links(
                    info.filename,
                    data.decode("utf-8", errors="strict"),
                    set(names),
                )

    return {
        "artifact": archive_path,
        "members": len(infos),
        "markdown_links_checked": checked_links,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit generated SoulMap ZIP and .skill artifacts without extraction."
    )
    parser.add_argument(
        "artifacts",
        nargs="*",
        default=list(DEFAULT_ARTIFACTS),
        help="Artifact paths to audit (default: generated ZIP and .skill).",
    )
    args = parser.parse_args(argv)
    try:
        results = [audit_artifact(path) for path in args.artifacts]
    except ArtifactSecurityError as exc:
        print(f"ERROR artifact security: {exc}", file=sys.stderr)
        return 1

    for result in results:
        print(
            f"PASS artifact security: {result['artifact']} "
            f"members={result['members']} "
            f"markdown_links={result['markdown_links_checked']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
