"""Audit shipped SoulMap skills for accidental implementation leakage."""

from __future__ import annotations

import argparse
from pathlib import Path

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


def _iter_shipped_markdown(repo_root: Path) -> list[Path]:
    root = repo_root / "skills"
    return sorted(root.rglob("*.md"))


def _line_number(token: object) -> int:
    """Return a best-effort one-based Markdown source line number."""
    source_map = getattr(token, "map", None)
    return int(source_map[0]) + 1 if source_map else 1


def _implementation_tokens(value: str) -> tuple[str, ...]:
    """Return implementation references that are meaningful in Markdown syntax."""
    lowered = value.lower()
    return tuple(token for token in _FORBIDDEN_TEXT if token.lower() in lowered)


def audit_markdown(relative_path: str | Path, text: str) -> list[str]:
    """Return implementation-leak findings using Markdown structure.

    Plain prose is allowed to discuss generic concepts such as Python or class.
    Implementation references are rejected when they point to repository/runtime
    surfaces or appear inside executable code constructs.
    """
    from markdown_it import MarkdownIt

    rel = Path(relative_path)
    findings: list[str] = []
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
                    f"{rel}:{line_no}: implementation token in code block: {reference!r}"
                )
            continue

        if token.type == "code_block":
            for reference in _implementation_tokens(token.content):
                findings.append(
                    f"{rel}:{line_no}: implementation token in code block: {reference!r}"
                )
            continue

        if token.type != "inline" or not token.children:
            continue

        for child in token.children:
            child_line = line_no
            if child.type == "code_inline":
                for reference in _implementation_tokens(child.content):
                    findings.append(
                        f"{rel}:{child_line}: implementation token in inline code: "
                        f"{reference!r}"
                    )
            elif child.type in {"link_open", "image"}:
                href_value = child.attrGet("href") or child.attrGet("src")
                href = href_value if isinstance(href_value, str) else ""
                for reference in _implementation_tokens(href):
                    findings.append(
                        f"{rel}:{child_line}: implementation reference in link target: "
                        f"{reference!r}"
                    )

        plain = token.content
        for reference in _implementation_tokens(plain):
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
                "skills/runtime/",
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


def _audit_file(path: Path, repo_root: Path) -> list[str]:
    return audit_markdown(
        path.relative_to(repo_root),
        path.read_text(encoding="utf-8"),
    )


def audit(repo_root: Path) -> list[str]:
    """Return every implementation-leak finding in shipped domain skills."""
    findings: list[str] = []
    for path in _iter_shipped_markdown(repo_root):
        findings.extend(_audit_file(path, repo_root))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Run the shipped-skill implementation boundary audit."""
    parser = argparse.ArgumentParser(
        description="Reject implementation leakage from shipped SoulMap skills."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    findings = audit(args.root.resolve())
    if findings:
        print("\n".join(findings))
        return 1
    print("Skill implementation boundary: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
