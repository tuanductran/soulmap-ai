"""Audit shipped SoulMap skills for accidental implementation leakage."""

from __future__ import annotations

import argparse
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT

_RUNTIME_DIR = Path("skills/runtime")
_ALLOWED_PYTHON_MENTION = Path("skills/safety/whitelist-blacklist-system.md")
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
    return [
        path
        for path in sorted(root.rglob("*.md"))
        if _RUNTIME_DIR not in path.relative_to(repo_root).parents
    ]


def audit_markdown(relative_path: str | Path, text: str) -> list[str]:
    """Return implementation-leak findings for one shipped Markdown document."""
    rel = Path(relative_path)
    findings: list[str] = []
    lines = text.splitlines()

    if "python" in text.lower() and rel != _ALLOWED_PYTHON_MENTION:
        for line_no, line in enumerate(lines, start=1):
            if "python" in line.lower():
                findings.append(
                    f"{rel}:{line_no}: implementation-language reference: Python"
                )

    fence = chr(96) * 3
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip().lower()
        if stripped.startswith(fence):
            language = stripped[len(fence) :].strip()
            if language in _EXECUTABLE_FENCES:
                findings.append(
                    f"{rel}:{line_no}: executable code fence is not allowed"
                )

        for token in _FORBIDDEN_TEXT:
            if token in line:
                findings.append(
                    f"{rel}:{line_no}: repository/implementation token: {token!r}"
                )

        if (
            ("from " in line and " import " in line)
            or stripped.startswith(("import ", "def ", "class "))
            or "__name__ ==" in line
        ):
            findings.append(f"{rel}:{line_no}: implementation syntax detected")

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
