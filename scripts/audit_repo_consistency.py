#!/usr/bin/env python3
"""Inventory stale path references and comment-cleanup candidates in tracked files."""

from __future__ import annotations

import argparse
import io
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
    "README.md",
    "readme.md",
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


def read_text(path: Path) -> str | None:
    """Read a tracked text file, skipping binary and non-UTF-8 content."""
    try:
        raw = path.read_bytes()
        if b"\0" in raw:
            return None
        return raw.decode("utf-8")
    except (OSError, UnicodeDecodeError):
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
        except (IndentationError, tokenize.TokenError):
            pass
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
    current = {path.relative_to(root).as_posix() for path in tracked_files(root)}
    return sorted(
        {item.strip() for item in output.splitlines() if item.strip()} - current
    )


def path_reference_hits(content: str, deleted_path: str) -> list[tuple[int, str, str]]:
    """Find exact deleted-path mentions and distinctive basename-only mentions."""
    basename = Path(deleted_path).name
    variants = [
        (deleted_path, "exact-path"),
        (deleted_path.replace("/", "\\"), "backslash-path"),
    ]
    if len(basename) >= 8 and basename not in GENERIC_BASENAMES:
        variants.append((basename, "basename-only"))
    hits: list[tuple[int, str, str]] = []
    for number, line in enumerate(content.splitlines(), start=1):
        for token, kind in variants:
            if token and token in line:
                hits.append((number, kind, line.strip()))
                break
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

    comment_count = 0
    path_count = 0
    if comments_enabled:
        print("COMMENT CANDIDATES (manual review; no automatic deletion)")
        for path in files:
            content = read_text(path)
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
                path.relative_to(root).as_posix(): read_text(path) for path in files
            }
            for deleted_path in removed:
                for current_path, content in contents.items():
                    if content is None:
                        continue
                    for number, kind, line in path_reference_hits(
                        content, deleted_path
                    ):
                        print(
                            f"{current_path}:{number}: {kind} -> {deleted_path}: {line}"
                        )
                        path_count += 1
            print(f"Deleted paths examined: {len(removed)}")
            print(f"Potential path references: {path_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
