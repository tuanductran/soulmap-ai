#!/usr/bin/env python3
"""Inventory stale path references and comment-cleanup candidates in tracked files."""

from __future__ import annotations

import argparse
import io
import posixpath
import re
import subprocess
import tokenize
from collections.abc import Sequence
from pathlib import Path

COMMENT_CANDIDATE = re.compile(
    r"\b(TODO|FIXME|HACK|XXX|TBD|WIP|deprecated|obsolete|temporarily|temporary|"
    r"remove after|kept for|phase\s+\d+)\b",
    re.IGNORECASE,
)
HASH_COMMENT_SUFFIXES = {
    ".py",
    ".pyi",
    ".sh",
    ".bash",
    ".zsh",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
}
CODE_SUFFIXES = {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java"}
COMMENTED_CODE = re.compile(
    r"^(?:if\s|elif\s|else:|return\s|raise\s|def\s|class\s|import\s|"
    r"from\s|for\s|while\s|try:|except(?:\s|:)|with\s|async\s+def\s|"
    r"assert\s|[A-Za-z_]\w*\s*=\s*(?:None|True|False|[\[{\d\"']))"
)
SLASH_COMMENT_SUFFIXES = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".css",
    ".scss",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".swift",
    ".kt",
    ".kts",
}
GENERIC_BASENAMES = {
    "__init__.py",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "readme.md",
    "SKILL.md",
    "index.md",
    "config.py",
    "constants.py",
    "utils.py",
    "types.py",
    "main.py",
    "Dockerfile",
}


def run_git(root: Path, *args: str) -> str:
    """Run a git command and return its UTF-8 output."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def tracked_files(root: Path) -> list[Path]:
    """Return tracked files that exist in the working tree."""
    names = run_git(root, "ls-files", "-z").split("\0")
    return [root / name for name in names if name and (root / name).is_file()]


def read_text(path: Path, limitations: list[str] | None = None) -> str | None:
    """Read a tracked text file, recording unreadable text as an audit limitation."""
    try:
        raw = path.read_bytes()
        if b"\0" in raw:
            return None
        return raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        if limitations is not None:
            limitations.append(
                f"{path}: unable to read tracked text file ({type(exc).__name__})"
            )
        return None


def comment_body(
    path: Path, line: str, in_html_comment: bool
) -> tuple[str | None, bool]:
    """Extract a whole-line comment body and track multiline HTML comments."""
    suffix = path.suffix.lower()
    stripped = line.lstrip()
    if suffix in {".md", ".mdx", ".html", ".htm", ".xml", ".svg"}:
        if in_html_comment or "<!--" in line:
            body = line.split("<!--", 1)[-1].split("-->", 1)[0]
            return body, "-->" not in line
        return None, False
    if suffix in HASH_COMMENT_SUFFIXES or path.name == "Dockerfile":
        return (stripped[1:], False) if stripped.startswith("#") else (None, False)
    if suffix in SLASH_COMMENT_SUFFIXES and stripped.startswith(
        ("/*", "*/", "//", "*")
    ):
        prefix = next(
            marker for marker in ("/*", "*/", "//", "*") if stripped.startswith(marker)
        )
        return stripped[len(prefix) :].lstrip(), False
    return None, False


def comment_candidates(path: Path, content: str) -> list[tuple[int, str]]:
    """Return review-only candidates from comments, never deleting anything."""
    findings: list[tuple[int, str]] = []
    suffix = path.suffix.lower()
    if suffix in {".py", ".pyi"}:
        try:
            tokens = tokenize.generate_tokens(io.StringIO(content).readline)
            for token in tokens:
                if token.type != tokenize.COMMENT:
                    continue
                body = token.string.lstrip("#").strip()
                marker_match = COMMENT_CANDIDATE.search(body)
                code_match = COMMENTED_CODE.search(body)
                if marker_match or code_match:
                    findings.append((token.start[0], token.string.strip()))
        except (IndentationError, tokenize.TokenError) as exc:
            raise RuntimeError(
                f"Unable to tokenize Python comments in {path}: {exc}"
            ) from exc
        return findings

    in_html_comment = False
    for number, line in enumerate(content.splitlines(), start=1):
        body, in_html_comment = comment_body(path, line, in_html_comment)
        if body is None:
            continue
        marker_match = COMMENT_CANDIDATE.search(body)
        code_match = suffix in CODE_SUFFIXES and COMMENTED_CODE.search(body.strip())
        if marker_match or code_match:
            findings.append((number, line.strip()))
    return findings


def deleted_paths(root: Path, base: str | None, history: bool) -> list[str]:
    """Find paths deleted in a comparison range or anywhere in reachable history."""
    if base:
        output = run_git(
            root, "diff", "--name-only", "--diff-filter=D", f"{base}...HEAD"
        )
    elif history:
        output = run_git(
            root, "log", "--all", "--diff-filter=D", "--name-only", "--format="
        )
    else:
        return []
    # Include tracked directories as current paths too. Git history can contain a
    # deleted file whose path was later reused as a directory (for example,
    # ".claude/hooks"); references to that live directory are not stale file paths.
    current: set[str] = set()
    for path in tracked_files(root):
        relative = path.relative_to(root)
        current.add(relative.as_posix())
        current.update(
            parent.as_posix() for parent in relative.parents if parent.as_posix() != "."
        )
    return sorted(
        {item.strip() for item in output.splitlines() if item.strip()} - current
    )


def path_reference_hits(
    content: str,
    deleted_path: str,
    *,
    source_path: Path | None = None,
    current_paths: set[str] | None = None,
    current_paths_by_basename: dict[str, set[str]] | None = None,
) -> list[tuple[int, str, str]]:
    """Find exact deleted-path mentions and distinctive basename-only mentions.

    When a line resolves to a current file with the same basename, do not also
    report it as a possible reference to a different historical path.
    """
    basename = Path(deleted_path).name
    variants = [
        (deleted_path, "exact-path"),
        (deleted_path.replace("/", "\\"), "backslash-path"),
    ]
    if len(basename) >= 8 and basename not in GENERIC_BASENAMES:
        variants.append((basename, "basename-only"))

    # Compile once per deleted path, not once per scanned line. Full-history
    # audits may inspect thousands of deleted paths across many tracked files.
    patterns = [
        (re.compile(rf"(?<![\w.-]){re.escape(token)}(?![\w-]|\.[A-Za-z0-9])"), kind)
        for token, kind in variants
        if token
    ]
    if source_path is not None and current_paths_by_basename is not None:
        same_basename_paths = current_paths_by_basename.get(basename, set()) - {
            deleted_path
        }
    elif source_path is not None:
        same_basename_paths = {
            path
            for path in current_paths or set()
            if Path(path).name == basename and path != deleted_path
        }
    else:
        same_basename_paths = set()
    current_path_patterns: list[re.Pattern[str]] = []
    same_directory_basename = False
    for path in same_basename_paths:
        tokens = {path, path.replace("/", "\\")}
        if source_path is not None:
            relative = posixpath.relpath(path, source_path.parent.as_posix())
            tokens.update({relative, relative.replace("/", "\\")})
            if relative == basename:
                same_directory_basename = True
        current_path_patterns.extend(
            re.compile(rf"(?<![\w.-]){re.escape(token)}(?![\w-]|\.[A-Za-z0-9])")
            for token in tokens
            if token and token != basename
        )

    hits: list[tuple[int, str, str]] = []
    for number, line in enumerate(content.splitlines(), start=1):
        for pattern, kind in patterns:
            if not pattern.search(line):
                continue
            if kind == "basename-only" and (
                same_directory_basename
                or any(current_pattern.search(line) for current_pattern in current_path_patterns)
            ):
                continue
            hits.append((number, kind, line.strip()))
            break
    return hits


def deleted_directories(root: Path, removed_paths: Sequence[str]) -> list[str]:
    """Return deleted ancestor directories that no longer contain tracked files."""
    current_directories: set[str] = set()
    for path in tracked_files(root):
        for parent in path.relative_to(root).parents:
            if parent.as_posix() != ".":
                current_directories.add(parent.as_posix())

    removed_directories: set[str] = set()
    for removed_path in removed_paths:
        for parent in Path(removed_path).parents:
            name = parent.as_posix()
            if name != "." and name not in current_directories:
                removed_directories.add(name)
    return sorted(removed_directories, key=lambda value: (value.count("/"), value))


def directory_reference_hits(
    content: str, deleted_directory: str
) -> list[tuple[int, str, str]]:
    """Find path-shaped or quoted references to a deleted directory.

    Deliberately require path separators or a quoted standalone root-directory
    token. This avoids treating ordinary prose mentions as stale path references.
    Findings remain candidates for manual review, not proof of dead code.
    """
    normalized = deleted_directory.replace("\\", "/").strip("/")
    path_pattern = re.compile(rf"(?<![\w./-])(?:\./)?{re.escape(normalized)}(?=[/\\])")
    basename = Path(normalized).name
    quoted_pattern = None
    if "/" not in normalized and basename:
        quoted_pattern = re.compile(
            rf"(?P<quote>['\"\x60]){re.escape(basename)}(?P=quote)"
        )

    hits: list[tuple[int, str, str]] = []
    for number, line in enumerate(content.splitlines(), start=1):
        if path_pattern.search(line):
            hits.append((number, "directory-path", line.strip()))
        elif quoted_pattern and quoted_pattern.search(line):
            hits.append((number, "quoted-directory-token", line.strip()))
    return hits


def main(argv: Sequence[str] | None = None) -> int:
    """Run the repository consistency inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--base", help="Compare HEAD with this base ref for deleted paths."
    )
    group.add_argument(
        "--history",
        action="store_true",
        help="Search all reachable Git history for deleted paths (may be noisy).",
    )
    parser.add_argument("--comments-only", action="store_true")
    parser.add_argument("--paths-only", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    files = tracked_files(root)
    comments_enabled = not args.paths_only
    paths_enabled = not args.comments_only

    current_paths = {path.relative_to(root).as_posix() for path in files}
    current_paths_by_basename: dict[str, set[str]] = {}
    for current_path in current_paths:
        current_paths_by_basename.setdefault(Path(current_path).name, set()).add(
            current_path
        )

    comment_count = 0
    path_count = 0
    limitations: list[str] = []
    if comments_enabled:
        print("COMMENT CANDIDATES (manual review; no automatic deletion)")
        for path in files:
            content = read_text(path, limitations)
            if content is None:
                continue
            for number, line in comment_candidates(path, content):
                print(f"{path.relative_to(root)}:{number}: {line}")
                comment_count += 1
        print(f"Comment candidates: {comment_count}")

    if paths_enabled:
        removed = deleted_paths(root, args.base, args.history)
        if not args.base and not args.history:
            print(
                "Deleted-path scan skipped: pass --base REF for a change-range audit "
                "or --history for all reachable Git history."
            )
        else:
            print(
                "POTENTIAL REFERENCES TO DELETED PATHS (manual classification required)"
            )
            contents = {
                path.relative_to(root).as_posix(): read_text(path, limitations)
                for path in files
            }
            for deleted_path in removed:
                for current_path, content in contents.items():
                    if content is None:
                        continue
                    for number, kind, line in path_reference_hits(
                        content,
                        deleted_path,
                        source_path=Path(current_path),
                        current_paths=current_paths,
                        current_paths_by_basename=current_paths_by_basename,
                    ):
                        print(
                            f"{current_path}:{number}: {kind} -> {deleted_path}: {line}"
                        )
                        path_count += 1

            removed_directories = deleted_directories(root, removed)
            directory_count = 0
            print("POTENTIAL REFERENCES TO DELETED DIRECTORIES")
            for directory in removed_directories:
                for current_path, content in contents.items():
                    if content is None:
                        continue
                    for number, kind, line in directory_reference_hits(
                        content, directory
                    ):
                        print(
                            f"{current_path}:{number}: {kind} -> {directory}/: {line}"
                        )
                        directory_count += 1
            print(f"Deleted paths examined: {len(removed)}")
            print(f"Deleted directories examined: {len(removed_directories)}")
            print(f"Potential path references: {path_count}")
            print(f"Potential directory references: {directory_count}")
    for limitation in sorted(set(limitations)):
        print(f"AUDIT LIMITATION: {limitation}")
    if limitations:
        print("INCOMPLETE: one or more tracked text files could not be inspected.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
