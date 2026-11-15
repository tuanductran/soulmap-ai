"""Audit every shipped Markdown file for repository and implementation leakage."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from soulmap.devtools.packaging.members import source_members
from soulmap.devtools.support.repo import REPO_ROOT

_FORBIDDEN_TEXT = (
    "src/soulmap/",
    ".py",
    ".claude/",
    ".github/",
    "tests/",
    "scripts/",
    "templates/",
    "library/",
    "pyproject.toml",
    "uv.lock",
    "pip install",
    "uv run",
    "pytest",
    "python -m",
)
_FORBIDDEN_LANGUAGES = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:python|javascript|typescript|java|c[+]{2}|c#|ruby|php|swift|kotlin|"
    r"rust|perl|scala|haskell|elixir|clojure|dart|lua|objective-c|sql)"
    r"(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_EXECUTABLE_FENCES = (
    "python",
    "py",
    "javascript",
    "js",
    "typescript",
    "ts",
    "bash",
    "sh",
    "shell",
    "zsh",
    "powershell",
)


def _iter_shipped_files(repo_root: Path) -> list[Path]:
    """Return every file eligible for either build artifact."""
    members = source_members(repo_root, include_plugin=True)
    return sorted(repo_root / member for member in members)


def _line_number(token: object) -> int:
    """Return a best-effort one-based Markdown source line number."""
    source_map = getattr(token, "map", None)
    return int(source_map[0]) + 1 if source_map else 1


def _implementation_tokens(value: str) -> tuple[str, ...]:
    """Return implementation references meaningful in Markdown syntax."""
    lowered = value.lower()
    return tuple(token for token in _FORBIDDEN_TEXT if token.lower() in lowered)


def audit_markdown(relative_path: str | Path, text: str) -> list[str]:
    """Return implementation-leak findings using Markdown structure."""
    from markdown_it import MarkdownIt

    rel = Path(relative_path)
    findings: list[str] = []

    for match in _FORBIDDEN_LANGUAGES.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        findings.append(
            f"{rel}:{line_no}: implementation language reference: {match.group(0)!r}"
        )

    parser = MarkdownIt("commonmark")
    tokens = parser.parse(text)

    for token in tokens:
        line_no = _line_number(token)

        if token.type == "fence":
            language = token.info.strip().split(maxsplit=1)[0].lower()
            if language in _EXECUTABLE_FENCES:
                findings.append(
                    f"{rel}:{line_no}: executable code fence is not allowed"
                )
            for reference in _implementation_tokens(token.content):
                findings.append(
                    f"{rel}:{line_no}: implementation token in code block: "
                    f"{reference!r}"
                )
            continue

        if token.type == "code_block":
            for reference in _implementation_tokens(token.content):
                findings.append(
                    f"{rel}:{line_no}: implementation token in code block: "
                    f"{reference!r}"
                )
            continue

        if token.type != "inline" or not token.children:
            continue

        for child in token.children:
            if child.type == "code_inline":
                for reference in _implementation_tokens(child.content):
                    findings.append(
                        f"{rel}:{line_no}: implementation token in inline code: "
                        f"{reference!r}"
                    )
            elif child.type in {"link_open", "image"}:
                href_value = child.attrGet("href") or child.attrGet("src")
                href = href_value if isinstance(href_value, str) else ""
                for reference in _implementation_tokens(href):
                    findings.append(
                        f"{rel}:{line_no}: implementation reference in link target: "
                        f"{reference!r}"
                    )

        for reference in _implementation_tokens(token.content):
            if reference in {"templates/", "library/"}:
                findings.append(
                    f"{rel}:{line_no}: repository-only reference: {reference!r}"
                )
            elif reference in {
                "src/soulmap/",
                ".claude/",
                ".github/",
                "tests/",
                "scripts/",
                "pyproject.toml",
                "uv.lock",
                ".py",
                "pip install",
                "uv run",
                "pytest",
                "python -m",
            }:
                findings.append(
                    f"{rel}:{line_no}: implementation reference: {reference!r}"
                )

    return findings


def audit_text(relative_path: str | Path, text: str) -> list[str]:
    """Reject implementation references in non-Markdown shipped text files."""
    rel = Path(relative_path)
    lowered = text.lower()
    findings: list[str] = []

    for match in _FORBIDDEN_LANGUAGES.finditer(text):
        line_no = text.count("\\n", 0, match.start()) + 1
        findings.append(
            f"{rel}:{line_no}: implementation language reference: {match.group(0)!r}"
        )

    for reference in _FORBIDDEN_TEXT:
        start = lowered.find(reference.lower())
        if start >= 0:
            line_no = text.count("\\n", 0, start) + 1
            findings.append(
                f"{rel}:{line_no}: implementation reference: {reference!r}"
            )

    return findings


def audit(repo_root: Path) -> list[str]:
    """Return implementation-leak findings across every build-eligible text file."""
    findings: list[str] = []
    for path in _iter_shipped_files(repo_root):
        relative = path.relative_to(repo_root)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_bytes().decode("utf-8", errors="ignore")

        if path.suffix.casefold() == ".md":
            findings.extend(audit_markdown(relative, content))
        else:
            findings.extend(audit_text(relative, content))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Run the shipped-Markdown implementation boundary audit."""
    parser = argparse.ArgumentParser(
        description="Reject implementation leakage from shipped SoulMap Markdown."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    findings = audit(args.root.resolve())
    if findings:
        print("\n".join(findings))
        return 1
    print("Shipped Markdown boundary: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
