from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from soulmap.devtools.support.markdown import resolve_markdown_inputs

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
_FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
_INLINE_CODE_RE = re.compile(r"`[^`]+`")


@dataclass(frozen=True)
class Issue:
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
    if _is_exempt(path, repo_root):
        return []

    issues: list[Issue] = []
    in_fence = False
    for line_no, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if _FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        searchable = _INLINE_CODE_RE.sub(" ", raw)
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
    issues: list[Issue] = []
    for path in resolve_markdown_inputs(repo_root, inputs):
        issues.extend(check_file(path, repo_root))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulmap check-case")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
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
