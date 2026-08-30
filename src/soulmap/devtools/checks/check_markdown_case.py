"""Canonical product and tool name casing checker.

Flags Markdown prose that writes a known product or tool name with the wrong
capitalization, such as "Soulmap" for "SoulMap". Code spans, fenced blocks, and
literal ``.md`` filename references (for example ``SOULMAP.md``, whose own
uppercase name would otherwise collide with the "SoulMap" rule) are skipped,
since they quote literal identifiers rather than prose. A wrong-case filename
inside a link target is check-links' job, not this checker's.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from soulmap.devtools.support.markdown import FenceTracker, resolve_markdown_inputs

_CASE_RULES: tuple[tuple[str, str], ...] = (
    ("SoulMap AI", "SoulMap AI"),
    ("SoulMap", "SoulMap"),
    ("GitHub", "GitHub"),
    ("Claude", "Claude"),
    ("Codex", "Codex"),
    ("Pyright", "Pyright"),
    ("Hypothesis", "Hypothesis"),
    ("Ruff", "Ruff"),
    ("lefthook", "lefthook"),
    ("Markdown", "Markdown"),
)

_PATH_EXEMPTIONS = {
    Path("CHANGELOG.md"),
    Path("CLAUDE.md"),
}
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_MARKDOWN_FILENAME_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*\.md\b")


@dataclass(frozen=True)
class Issue:
    """One casing violation.

    Attributes:
        path: File the violation was found in.
        line: 1-indexed line the violation is on.
        message: Description naming the term found and the canonical form.
    """

    path: Path
    line: int
    message: str


def _pattern_for(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    return re.compile(
        rf"(?<![A-Za-z0-9_/-])({escaped})(?![A-Za-z0-9_/-])", re.IGNORECASE
    )


_COMPILED_RULES = tuple(
    (_pattern_for(match_text), canonical) for match_text, canonical in _CASE_RULES
)


def _is_exempt(path: Path, repo_root: Path) -> bool:
    rel = path.resolve().relative_to(repo_root)
    return rel in _PATH_EXEMPTIONS


def check_file(path: Path, repo_root: Path) -> list[Issue]:
    """Check one Markdown file for canonical-casing violations.

    Args:
        path: Markdown file to check.
        repo_root: Repository root, used to test the file against the
            exemption list.

    Returns:
        Every violation found, in line order. Empty for an exempt file or one
        that conforms.
    """
    if _is_exempt(path, repo_root):
        return []

    issues: list[Issue] = []
    fence = FenceTracker()
    for line_no, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if fence.consume(raw):
            continue

        searchable = _INLINE_CODE_RE.sub(" ", raw)
        searchable = _MARKDOWN_FILENAME_RE.sub(" ", searchable)
        matched_spans: list[tuple[int, int]] = []
        for pattern, canonical in _COMPILED_RULES:
            for match in pattern.finditer(searchable):
                span = match.span(1)
                if any(
                    not (span[1] <= existing[0] or span[0] >= existing[1])
                    for existing in matched_spans
                ):
                    continue
                found = match.group(1)
                if found == canonical:
                    matched_spans.append(span)
                    continue
                matched_spans.append(span)
                issues.append(
                    Issue(
                        path,
                        line_no,
                        f"Canonical case mismatch: found '{found}', expected '{canonical}'",
                    )
                )
    return issues


def check_repo(repo_root: Path, inputs: list[str] | None = None) -> list[Issue]:
    """Check Markdown files for canonical-casing violations.

    Args:
        repo_root: Repository root.
        inputs: Files or directories to check, or None for the whole
            repository.

    Returns:
        Every violation found across the checked files.
    """
    issues: list[Issue] = []
    for path in resolve_markdown_inputs(repo_root, inputs):
        issues.extend(check_file(path, repo_root))
    return issues


def main(argv: list[str] | None = None) -> int:
    """Run the canonical-casing check from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when every file conforms, 1 when any violation is found.
    """
    parser = argparse.ArgumentParser(prog="soulmap check-case")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(),
        help="Repo root (default: current directory).",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional Markdown files or directories to check.",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    issues = check_repo(repo_root, args.paths)
    if not issues:
        return 0

    for issue in issues:
        rel = issue.path.resolve().relative_to(repo_root)
        print(f"{rel}:{issue.line}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
